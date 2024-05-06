import os
BASE_DIR = os.getenv("HOME")
DATA_DIR = os.path.join(BASE_DIR, "assets", "data")
INDEX_DIR = os.path.join(DATA_DIR,"index")
DB_DIR = os.path.join(DATA_DIR, "chroma_db")
RAW_DATA_DIR=os.path.join(DATA_DIR, "raw")
EVAL_DATA_DIR = os.path.join(DATA_DIR, "questions")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
VECTORDB_COLLECTION ="quickstart-ollama"
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL")