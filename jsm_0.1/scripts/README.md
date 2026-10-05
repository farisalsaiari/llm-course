python -m scripts.acquisition
python -m scripts.inspection

python -m scripts.provenance
python -m scripts.provenance_review ali-hassan-20261005T062816Z-7a7793a1 allowed owned_data
python -m scripts.provenance

python -m scripts.ingestion

python -m scripts.extraction

python -m scripts.cleaning
python -m scripts.normalization
python -m scripts.filtering
python -m scripts.deduplication

python -m scripts.dataset_building

python -m scripts.tokenizer_training

for test : 
python -c "from paths import TOKENIZER_PATH; from src.tokenization.tokenizer import Tokenizer; t=Tokenizer.load(TOKENIZER_PATH); text='مرحبا بالعالم'; ids=t.encode(text, add_special_tokens=True); print(ids); print(t.decode(ids)); assert t.decode(ids)==text; print('PASS')"

python -m scripts.tokenize_dataset

python -m scripts.train

python -m scripts.inference "علي حسن"
python -m scripts.inference "مشروع"

python -m scripts.evaluate

python -m scripts.serve
http://127.0.0.1:8000/docs


python -m scripts.model_stats