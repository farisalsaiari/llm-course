storage/uploads/
        ↓
Acquisition
  └─ connector: local-uploads
        ↓
storage/incoming/batches/
        ↓
Inspection
        ↓
Rights / Provenance Gate
        ↓
Ingestion
        ↓
storage/raw/



---


External Data
    ↓
1. Acquisition ✅
    ↓
2. Inspection ✅
    ↓
3. Provenance / Rights Gate
    ↓
4. Ingestion
    ↓
5. Extraction
    ↓
6. Preprocessing
      ├── Cleaning
      ├── Normalization
      ├── Filtering
      └── Deduplication
    ↓
7. Dataset Building
      ├── document boundaries
      ├── train/validation/test
      └── dataset manifests
    ↓
8. Tokenizer Training
    ↓
9. Tokenization + Sharding
    ↓
10. Model Architecture
    ↓
11. Pretraining
    ↓
12. Checkpoints / Resume
    ↓
13. Evaluation
    ↓
14. Inference
    ↓
15. Serving
    ↓
LIVE MODEL