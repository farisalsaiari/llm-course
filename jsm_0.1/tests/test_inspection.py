"""Inspection contract tests; fixtures never enter the live incoming catalog."""
import codecs
import hashlib
import io
import json
import os
import stat
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from src.inspection.checks import (
    _scan_snapshots, apply_malware_result, inspect_artifact, scan_malware_batch,
)
from src.inspection.config import load_inspection_config, validate_inspection_config
from src.inspection.inspector import inspect_batch
from src.inspection.quarantine import quarantine_batch
from src.inspection.report import completed_batches, publish_record, write_inspection_report
from src.inspection.result import InspectionDecision as D, MalwareScanResult, MalwareScanStatus as M, more_restrictive_decision


def zip_bytes(members):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            archive.writestr(name, data)
    return output.getvalue()


def office_members(extra=()):
    return [('[Content_Types].xml', '<Types/>'), ('_rels/.rels', '<Relationships/>'),
            ('word/document.xml', '<document><body>hello</body></document>'), *extra]


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.batch = self.root / 'batch-test'
        (self.batch / 'objects').mkdir(parents=True)
        self.policy = load_inspection_config()
        self.policy['require_malware_scan'] = False
        self.items = []
        self.scanners = patch('src.inspection.checks.shutil.which', return_value=None)
        self.scanners.start()
        self.addCleanup(self.scanners.stop)

    def add(self, name, data):
        path = self.batch / 'objects' / f'{len(self.items):03d}-{name}'
        path.write_bytes(data)
        item = dict(artifact_id=f'a{len(self.items)}', original_filename=name,
                    stored_relative_path=path.relative_to(self.batch).as_posix(),
                    size_bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.items.append(item)
        return item, path

    def manifest(self, **updates):
        record = dict(schema_version='1.0.0', record_type='incoming_source_batch',
                      batch_id=self.batch.name, source={}, license={}, artifacts=self.items)
        record.update(updates)
        data = json.dumps(record).encode()
        (self.batch / 'source.json').write_bytes(data)
        (self.batch / 'source.json.sha256').write_text(hashlib.sha256(data).hexdigest())

    def inspect(self, item):
        return inspect_artifact(self.batch, item, self.policy, self.policy['max_batch_size_bytes'])

    def run_batch(self):
        self.manifest()
        return inspect_batch(self.batch, self.policy)

    def test_decision_never_downgrades(self):
        for candidate in D:
            self.assertEqual(more_restrictive_decision(D.REJECTED, candidate), D.REJECTED)
        self.assertEqual(more_restrictive_decision(D.ACCEPTED, D.QUARANTINED), D.QUARANTINED)

    def test_mixed_batch_and_actual_duplicate_hashes(self):
        self.add('good.txt', b'hello\n')
        self.add('copy.txt', b'hello\n')
        self.add('fake.pdf', b'hello\n')
        self.add('program.exe', b'MZprogram')
        result = self.run_batch()
        self.assertTrue(result.batch_valid)
        self.assertEqual([a.decision for a in result.artifacts], [D.ACCEPTED, D.ACCEPTED, D.QUARANTINED, D.REJECTED])
        self.assertEqual(result.summary['accepted'], 2)
        self.assertEqual(result.duplicate_groups[0]['count'], 3)

    def test_artifact_corruption_does_not_block_sibling(self):
        item, path = self.add('changed.txt', b'hello')
        path.write_bytes(b'world')
        self.add('good.txt', b'fine')
        result = self.run_batch()
        self.assertTrue(result.batch_valid)
        self.assertEqual(result.artifacts[0].decision, D.QUARANTINED)
        self.assertEqual(result.artifacts[1].decision, D.ACCEPTED)
        self.assertEqual(result.artifacts[0].sha256, hashlib.sha256(b'world').hexdigest())

    def test_invalid_manifest_gates_all_content(self):
        self.add('good.txt', b'hello')
        for changes in ({'batch_id': 'other'}, {'artifacts': [None]}, {'artifacts': []},
                        {'source': []}, {'schema_version': 'unknown'}):
            with self.subTest(changes=changes):
                self.manifest(**changes)
                with patch('src.inspection.inspector.inspect_artifact') as inspect:
                    result = inspect_batch(self.batch, self.policy)
                self.assertFalse(result.batch_valid)
                self.assertEqual(result.artifacts, ())
                inspect.assert_not_called()

    def test_checksum_mismatch(self):
        self.add('good.txt', b'hello')
        self.manifest()
        with (self.batch / 'source.json').open('ab') as stream:
            stream.write(b' ')
        self.assertFalse(inspect_batch(self.batch, self.policy).batch_valid)

    def test_duplicate_manifest_ids(self):
        item, _ = self.add('good.txt', b'hello')
        self.items.append(item.copy())
        self.assertFalse(self.run_batch().batch_valid)

    def test_traversal_is_artifact_rejection(self):
        item, _ = self.add('bad.txt', b'hello')
        for path in ('../outside.txt', '/etc/passwd', 'objects/../source.json', 'objects\\x.txt', 'objects/C:x.txt'):
            with self.subTest(path=path):
                item['stored_relative_path'] = path
                self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_links_and_nonregular_files(self):
        item, path = self.add('link.txt', b'hello')
        path.unlink()
        path.symlink_to(self.root / 'nonexistent')
        result = self.inspect(item)
        self.assertEqual(result.decision, D.REJECTED)
        self.assertTrue(result.is_symlink)
        path.unlink()
        path.mkdir()
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_symlink_parent(self):
        item, path = self.add('good.txt', b'hello')
        objects = self.batch / 'objects'
        objects.rename(self.root / 'outside')
        objects.symlink_to(self.root / 'outside', target_is_directory=True)
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO')
    def test_fifo_not_opened(self):
        item, path = self.add('fifo.txt', b'hello')
        path.unlink()
        os.mkfifo(path)
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_missing_and_empty(self):
        item, path = self.add('missing.txt', b'hello')
        path.unlink()
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
        item, _ = self.add('empty.pdf', b'')
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)

    def test_oversized_file_not_hashed(self):
        item, _ = self.add('huge.txt', b'hello')
        self.policy['max_file_size_bytes'] = 4
        with patch('src.inspection.checks.stream_hash') as hash_file:
            self.assertEqual(self.inspect(item).decision, D.REJECTED)
        hash_file.assert_not_called()

    def test_budget_only_rejects_overflow(self):
        self.add('a.txt', b'1234')
        self.add('b.txt', b'1234')
        self.add('c.txt', b'1')
        self.policy['max_batch_size_bytes'] = 5
        self.assertEqual([a.decision for a in self.run_batch().artifacts], [D.ACCEPTED, D.REJECTED, D.ACCEPTED])
        self.policy['max_batch_size_bytes'] = 100
        self.policy['max_files_per_batch'] = 1
        self.assertEqual([a.decision for a in self.run_batch().artifacts], [D.ACCEPTED, D.REJECTED, D.REJECTED])

    def test_text_encodings_statistics(self):
        for encoding in ('utf-8', 'utf-8-sig', 'utf-16'):
            with self.subTest(encoding=encoding):
                item, _ = self.add('arabic.txt', 'مرحبا\r\nworld\nend'.encode(encoding))
                result = self.inspect(item)
                self.assertEqual(result.decision, D.ACCEPTED, result.errors)
                self.assertEqual(result.encoding, encoding)
                self.assertEqual((result.character_count, result.line_count, result.max_line_characters), (16, 3, 5))

    def test_late_invalid_utf8_and_controls(self):
        for data in (b'a' * 70000 + b'\xff', b'a' * 70000 + b'\x00'):
            item, _ = self.add('bad.txt', data)
            self.assertEqual(self.inspect(item).decision, D.QUARANTINED)

    def test_line_limit_and_chunk_boundary(self):
        item, _ = self.add('lines.txt', b'a' * 65535 + b'\r\nlast')
        self.policy['max_line_characters'] = 65534
        result = self.inspect(item)
        self.assertEqual(result.decision, D.QUARANTINED)
        self.assertEqual(result.line_count, 2)
        self.assertEqual(result.max_line_characters, 65535)

    def test_structured_json(self):
        for suffix, data, expected in (('.json', b'{"a":1}', D.ACCEPTED), ('.json', b'{bad}', D.QUARANTINED),
                                      ('.jsonl', b'{"a":1}\n{bad}', D.QUARANTINED), ('.json', b'NaN', D.QUARANTINED)):
            item, _ = self.add('data' + suffix, data)
            self.assertEqual(self.inspect(item).decision, expected)

    def test_content_disguised_executable(self):
        item, _ = self.add('program.pdf', b'MZpayload')
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_binary_garbage(self):
        item, _ = self.add('bad.txt', bytes(range(256)))
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)

    def test_safe_docx(self):
        item, _ = self.add('safe.docx', zip_bytes(office_members()))
        self.assertEqual(self.inspect(item).decision, D.ACCEPTED)

    def test_archive_attacks(self):
        for name in ('../escape', '/absolute', 'C:/windows', 'a\\b', 'word/vbaProject.bin',
                     'word/embeddings/data.bin', 'word/payload.exe', 'word/payload.dll'):
            with self.subTest(name=name):
                item, _ = self.add('bad.docx', zip_bytes(office_members([(name, 'payload')])))
                self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_archive_symlink(self):
        link = zipfile.ZipInfo('word/link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        item, _ = self.add('link.docx', zip_bytes(office_members([(link, '../outside')])))
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_archive_limits(self):
        for key in ('max_archive_files', 'max_archive_member_bytes', 'max_uncompressed_bytes', 'max_compression_ratio'):
            with self.subTest(key=key):
                policy = self.policy.copy()
                self.policy[key] = 1
                item, _ = self.add('large.docx', zip_bytes(office_members([('large.txt', 'a' * 10000)])))
                self.assertEqual(self.inspect(item).decision, D.REJECTED)
                self.policy = policy

    def test_archive_missing_member_and_corruption(self):
        for data in (zip_bytes([('other.xml', '<root/>')]), b'PKgarbage'):
            item, _ = self.add('bad.docx', data)
            self.assertEqual(self.inspect(item).decision, D.QUARANTINED)

    def test_other_supported_document_containers(self):
        fixtures = {
            'xlsx': [('[Content_Types].xml', '<Types/>'), ('_rels/.rels', '<Relationships/>'), ('xl/workbook.xml', '<workbook/>')],
            'pptx': [('[Content_Types].xml', '<Types/>'), ('_rels/.rels', '<Relationships/>'), ('ppt/presentation.xml', '<presentation/>')],
            'odt': [('mimetype', 'application/vnd.oasis.opendocument.text'), ('content.xml', '<document-content/>')],
            'ods': [('mimetype', 'application/vnd.oasis.opendocument.spreadsheet'), ('content.xml', '<document-content/>')],
            'epub': [('mimetype', 'application/epub+zip'), ('META-INF/container.xml', '<container/>')],
        }
        for suffix, members in fixtures.items():
            with self.subTest(suffix=suffix):
                item, _ = self.add('safe.' + suffix, zip_bytes(members))
                result = self.inspect(item)
                self.assertEqual(result.decision, D.ACCEPTED, result.errors)

    def test_encrypted_archive_and_crc_failure(self):
        data = bytearray(zip_bytes(office_members()))
        for signature, flag_offset in ((b'PK\x03\x04', 6), (b'PK\x01\x02', 8)):
            offset = 0
            while (offset := data.find(signature, offset)) >= 0:
                data[offset + flag_offset] |= 1
                offset += 4
        item, _ = self.add('encrypted.docx', data)
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
        data = bytearray(zip_bytes(office_members()))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            info = archive.getinfo('word/document.xml')
            offset = info.header_offset + 30 + len(info.filename.encode()) + len(info.extra)
        data[offset] ^= 0xff
        item, _ = self.add('crc.docx', data)
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)

    def test_external_relationships(self):
        rels = "<Relationships><Relationship TargetMode = 'External' Target='https://example.com'/></Relationships>"
        item, _ = self.add('external.docx', zip_bytes(office_members([('word/_rels/document.xml.rels', rels)])))
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_xml_declarations_in_utf16_and_beyond_prefix(self):
        for data in ('<!DOCTYPE root [<!ENTITY x "abc">]><root>&x;</root>'.encode('utf-16'),
                     b' ' * 1000100 + b'<!DOCTYPE root><root/>'):
            item, _ = self.add('unsafe.xml', data)
            self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_xml_malformed_and_depth(self):
        item, _ = self.add('bad.xml', b'<root>')
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
        self.policy['max_xml_depth'] = 2
        item, _ = self.add('deep.xml', b'<a><b><c/></b></a>')
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_pdf_active_names_and_missing_validator(self):
        for name in (b'JavaScript', b'JS', b'J#53', b'Launch', b'EmbeddedFile', b'OpenAction', b'AA'):
            item, _ = self.add('active.pdf', b'%PDF-1.4\n/' + name + b' 1\nstartxref\n0\n%%EOF')
            self.assertEqual(self.inspect(item).decision, D.REJECTED)
        item, _ = self.add('plain.pdf', b'%PDF-1.4\n/AAPL:Keywords 1\nstartxref\n0\n%%EOF')
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
        self.policy['require_deep_container_inspection'] = False
        result = self.inspect(item)
        self.assertEqual(result.decision, D.ACCEPTED)
        self.assertIn('pdf_validator_unavailable', result.flags)

    def test_html_rtf_and_legacy(self):
        for name, data, expected in [('page.html', b'<html><body>hello</body></html>', D.ACCEPTED),
                                     ('page.html', b'<html><script>alert(1)</script></html>', D.REJECTED),
                                     ('safe.rtf', b'{\\rtf1 hello}', D.ACCEPTED),
                                     ('bad.rtf', b'{\\rtf1 \\object thing}', D.REJECTED),
                                     ('legacy.doc', b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1xxx', D.QUARANTINED)]:
            item, _ = self.add(name, data)
            self.assertEqual(self.inspect(item).decision, expected)

    def test_scanner_unavailable_never_clean(self):
        self.add('good.txt', b'hello')
        self.policy['require_malware_scan'] = True
        result = self.run_batch().artifacts[0]
        self.assertEqual(result.decision, D.QUARANTINED)
        self.assertEqual(result.malware_scan_status, M.UNAVAILABLE)

    def test_scanner_batch_fallback_and_infection(self):
        paths = [self.root / '1.txt', self.root / '2.txt']
        def run(command, **kwargs):
            self.assertNotIn('shell', kwargs)
            self.assertEqual(command[-2:], list(map(str, paths)))
            if command[0] == 'clamdscan':
                return subprocess.CompletedProcess(command, 2, '', 'daemon unavailable')
            return subprocess.CompletedProcess(command, 1, f'{paths[0]}: OK\n{paths[1]}: Eicar FOUND\n', '')
        with patch('src.inspection.checks.shutil.which', side_effect=lambda name: name), patch('src.inspection.checks.subprocess.run', side_effect=run) as scanner:
            result = _scan_snapshots(paths, self.policy)
        self.assertEqual(scanner.call_count, 2)
        self.assertEqual(result[paths[0]].status, M.CLEAN)
        self.assertEqual(result[paths[1]].status, M.INFECTED)

    def test_scanner_missing_verdict_timeout_and_error(self):
        paths = [self.root / '1.txt']
        for response in (subprocess.CompletedProcess([], 0, '', ''), subprocess.CompletedProcess([], 2, f'{paths[0]}: OK\n', 'failed')):
            with patch('src.inspection.checks.shutil.which', return_value='scanner'), patch('src.inspection.checks.subprocess.run', return_value=response):
                self.assertEqual(_scan_snapshots(paths, self.policy)[paths[0]].status, M.ERROR)
        with patch('src.inspection.checks.shutil.which', return_value='scanner'), patch('src.inspection.checks.subprocess.run', side_effect=subprocess.TimeoutExpired('scanner', 1)):
            self.assertEqual(_scan_snapshots(paths, self.policy)[paths[0]].status, M.ERROR)

    def test_infected_decision_and_changed_snapshot(self):
        item, path = self.add('good.txt', b'hello')
        result = self.inspect(item)
        infected = apply_malware_result(result, MalwareScanResult(M.INFECTED, 'test', 'Eicar'), self.policy)
        self.assertEqual(infected.decision, D.REJECTED)
        clean = apply_malware_result(infected, MalwareScanResult(M.CLEAN, 'test'), self.policy)
        self.assertEqual(clean.decision, D.REJECTED)
        path.write_bytes(b'world')
        self.assertEqual(scan_malware_batch(self.batch, [result], self.policy)[item['artifact_id']].status, M.ERROR)

    def test_malware_chunks_bound_bytes_and_count(self):
        artifacts = [self.inspect(self.add(f'{i}.txt', b'hello')[0]) for i in range(5)]
        self.policy['max_malware_chunk_bytes'] = 10
        self.policy['malware_chunk_size'] = 3
        def scan(paths, policy):
            self.assertLessEqual(sum(p.stat().st_size for p in paths), 10)
            return {p: MalwareScanResult(M.CLEAN, 'test') for p in paths}
        with patch('src.inspection.checks._scan_snapshots', side_effect=scan) as scanner:
            result = scan_malware_batch(self.batch, artifacts, self.policy)
        self.assertEqual(scanner.call_count, 3)
        self.assertEqual(len(result), 5)

    def test_reports_immutable_and_quarantine_references(self):
        self.add('good.txt', b'hello')
        self.add('bad.pdf', b'fake')
        result = self.run_batch()
        before = {p: p.read_bytes() for p in self.batch.rglob('*') if p.is_file()}
        catalog = self.root / 'catalog'
        one = write_inspection_report(self.batch, result, catalog)
        two = write_inspection_report(self.batch, result, catalog)
        self.assertNotEqual(one, two)
        self.assertEqual(hashlib.sha256(one.read_bytes()).hexdigest(), one.with_suffix('.json.sha256').read_text().strip())
        record = json.loads(one.read_text())
        self.assertEqual(record['next_stage'], 'ingestion')
        self.assertEqual(record['eligible_artifact_ids'], ['a0'])
        quarantine = quarantine_batch(self.batch, result, one.parent.name, self.root / 'quarantine')
        self.assertEqual(json.loads(quarantine.read_text())['artifacts'][0]['artifact_id'], 'a1')
        with self.assertRaises(FileExistsError):
            publish_record(catalog, one.parent.name, 'manifest.json', {})
        self.assertEqual(before, {p: p.read_bytes() for p in self.batch.rglob('*') if p.is_file()})
        self.assertIn(str(self.batch), completed_batches(self.policy, catalog, self.root / 'quarantine'))
        self.assertNotIn(str(self.batch), completed_batches(self.policy, catalog, self.root / 'missing-quarantine'))
        changed = {**self.policy, 'max_line_characters': 17}
        self.assertNotIn(str(self.batch), completed_batches(changed, catalog))

    def test_bad_config_rejected(self):
        for key, value in [('max_file_size_bytes', True), ('max_line_characters', 0),
                           ('max_compression_ratio', float('inf')), ('require_malware_scan', 'yes'),
                           ('unknown_file_policy', 'accept'), ('expected_mime_types', {})]:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Inspection config'):
                validate_inspection_config({**self.policy, key: value})


if __name__ == '__main__':
    unittest.main()
