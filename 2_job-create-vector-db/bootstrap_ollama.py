## Bootstrap our OLLAMA Project
## We just set it up install the requirements and run ollama serve. 
import os
import sys
import subprocess
import utils.logging_config
import importlib
importlib.reload(utils.logging_config)

# Get the shared logger
from utils.logging_config import get_logger
logger = get_logger(__name__)

from utils import llm_helper
import shutil
## Copy the init.py file to overcome the SQLLite3 issue reported in Chromadb
# More details here : https://docs.trychroma.com/troubleshooting
source_file = '/home/cdsw/utils/sqlite_init.py'
destination_file = '/home/cdsw/.local/lib/python3.11/site-packages/chromadb/__init__.py'

try:
    shutil.copy2(source_file, destination_file)
    logger.info(f"INFO:File copied successfully from {source_file} to {destination_file}")
except shutil.Error as e:
    print(f"Error occurred while copying file for ChromadB setup: {e}")
    sys.exit(1)
except IOError as e:
    print(f"Error occurred while accessing file for ChromadB setup: {e}")
    sys.exit(1)

# for Vectorstore index
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb

## Setup the logger for debug
import sys
sys.path.append('/home/cdsw/utils')



# check if correct runtime is used else exit
llm_helper.validate_runtime()

logger.info("INFO: Running the Bootstrap")
## Let us setup Vectorindex for Vectorstoreindex
embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

#make sure that you ave run the site_scrapper.py Job to pull data in the raw directory 
logger.info("INFO: Reading the data")
# reading up Paul Graham
#documents = SimpleDirectoryReader("~/data/paul_graham/").load_data()
# Reading up Zerodha Varsity data.
documents = SimpleDirectoryReader("/home/cdsw/assets/data/raw/").load_data()
db = chromadb.PersistentClient(path="/home/cdsw/assets/data/chroma_db")
#db.reset()
chroma_collection = db.get_or_create_collection("quickstart-ollama")


logger.info("INFO:Setting up the vector Store")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, embed_model=embed_model
)
