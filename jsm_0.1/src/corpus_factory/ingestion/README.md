Distributed Ingestion
وظيفتها:
تقرأ الملفات الخام على عدة workers بدل worker واحد.

مثلاً:
1,000,000 files
↓
Worker 1 → files 1–100000
Worker 2 → files 100001–200000
Worker 3 → ...

Raw Storage
    ↓
Dispatcher
    ↓
┌────────┬────────┬────────┐
│Worker 1│Worker 2│Worker 3│
└────────┴────────┴────────┘
    ↓        ↓        ↓
 Readers / Extraction
    ↓
 Documents

 ---

 data/raw
↓
loader.py
↓
dispatcher.py
↓
عدة workers
↓
worker.py
↓
txt_reader.py
↓
document