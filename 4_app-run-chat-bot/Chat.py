
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext,  load_index_from_storage
from llama_index.core import Settings
from IPython.display import Markdown, display
import chromadb
## Run Ollama as a background process
import ollama
import os
import sys
import time
import subprocess
import psutil

#sys.path.append('/home/cdsw/utils')
import imp
#import utils.logging_config
#imp.reload(utils.logging_config)

#chainlit is our chat platform
import chainlit as cl

# Get the shared logger
from utils.logging_config import get_logger
logger = get_logger(__name__)
from utils.llm_helper import (
  is_process_running,
  validate_runtime,
  start_ollama_service, 
  test_ollama_model,
  initialize_llm_settings,
  )

#validate the right runtime is selected
validate_runtime()
# Check if the 'ollama' process is already running

if is_process_running('ollama'):
  logger.info(f"'ollama' is already running in background.")
else:
  start_ollama_service()
# Test a model, llama2 is also the default, so works without parameters
test_ollama_model(model="llama2")
  
#We will use Chainlit for our conversations

@cl.on_chat_start
async def start():

  
  logger.info("INFO : Inside On chat start")

  initialize_llm_settings(model="llama2")
  # load index from disk: Assumes that the bootstrap.py job has been run
  db2 = chromadb.PersistentClient(path="/home/cdsw/assets/data/chroma_db")
  chroma_collection = db2.get_or_create_collection("quickstart-ollama")
  vector_store = ChromaVectorStore(chroma_collection=chroma_collection)


  # we load the data saved in the vectorstore
  storage_context = StorageContext.from_defaults(vector_store=vector_store)
  logger.info("INFO:Loading the Index")
  index = VectorStoreIndex.from_vector_store(
    vector_store, storage_context=storage_context)  

  # Let us Configure the Chat Engine
  from llama_index.core.memory import ChatMemoryBuffer

  memory = ChatMemoryBuffer.from_defaults(token_limit=32000)
#  chat_engine = index.as_chat_engine()
  chat_engine = index.as_chat_engine(
      chat_mode="context",
      memory=memory,
      system_prompt=(
          "You are a chatbot, able to have normal interactions, as well as talk"
          " about Personal Finance"
      ),
  )
  logger.info(f"INFO: Chat Engine Created : type {type(chat_engine)}")

  response = chat_engine.chat("Hello")

  logger.info(f"INFO : Inside On chat start: Response from Query Engine{response}")
  
  #set up Chainlit session
  cl.user_session.set("chat_engine", chat_engine)
  image = cl.Image(path="/home/cdsw/assets/images/Llama2.jpg", name="image1", display="inline")

  # Attach the image to the message
  await cl.Message(
      content="You have started a chat with LLama2 Model augmented for Personal Finance.\n This SHOULD NOT be construed as Investment Advise!",
      elements=[image],
  ).send()
  
@cl.on_message
async def main(message: cl.Message):
    
  logger.info(f"INFO : Inside On Message:")  
  
  #show processing the message 
  await cl.Message(content="").send()
  
  # get the context
  chat_engine = cl.user_session.get("chat_engine") # type: RetrieverQueryEngine
  response_stream = await cl.make_async(chat_engine.stream_chat)(message.content)
  logger.info(f"INFO:{response_stream}")

  msg = cl.Message(content="")  
  for token in response_stream.response_gen:
    await msg.stream_token(token)
  await msg.send()

@cl.on_stop
async def on_stop():
  logger.info(f"INFO : Inside On Stop:")  
  
  await cl.Message(content="").send()
  chat_engine = cl.user_session.get("chat_engine") # type: RetrieverQueryEngine
  chat_engine.reset()
  
@cl.on_chat_end
async def on_chat_end():
  logger.info(f"INFO : Inside On End:")

  await cl.Message(content="").send()
  chat_engine = cl.user_session.get("chat_engine") # type: RetrieverQueryEngine
  chat_engine.reset()
  
  