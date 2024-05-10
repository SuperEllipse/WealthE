import os
import sys
import time
import subprocess
import psutil
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.fastembed import FastEmbedEmbedding
sys.path.append('/home/cdsw/utils')
import imp
import logging_config
imp.reload(logging_config)
from utils.configs import DEFAULT_LLM, OLLAMA_BASE_URL, DEFAULT_EMBEDDING_MODEL
# Get the shared logger
from logging_config import get_logger
logger = get_logger(__name__)


def validate_runtime():
  """
  Validate if the right runtme is used for the application. The session/job/application must use ollama runtime
  """
  try:
      result = subprocess.run(['ollama', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      if result.returncode != 0 and "/bin/bash: ollama: command not found" in result.stderr:
          raise Exception("The 'ollama' command is not installed or not found in the system PATH.")
      else:
          print(result.stdout)
        


  except Exception as e:
      print(f"Error: {e}")
      print (f"You need touse a Runtime with ollama to make this application work. Have you chosen the right runtime ?")
      sys.exit(1)  # Exit with a non-zero status code

  logger.info("INFO : ollama exists")
    
def is_process_running(process_name):
  """
  Check if a process with the given name is running.
  """
  for proc in psutil.process_iter(['name']):
    try:
      if process_name.lower() == proc.info['name'].lower():
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass
  return False

def terminate_processes(process_name):
    """
    Terminates all running processes with names containing the given substring.

    Args:
        process_name (str): The substring of the process name to search for.

    Returns:
        int: The number of processes terminated.
    """
    terminated_count = 0

    for proc in psutil.process_iter(['name']):
        try:
            # Check if the process name contains the substring (case-insensitive)
            if process_name.lower() in proc.info['name'].lower():
                proc.terminate()
                terminated_count += 1
                print(f"Terminated process: {proc.info['name']}, pid={proc.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return terminated_count

import ollama
def start_ollama_service(log_file=None):
    """
    Let us start the ollama service. we terminate any zombie processes that did not shutdown 
    First check if the entrypoint.sh exists in container
    This file is copied as a part of docker image. 
    INPUT : log_file : Non mandatory, only if you want to get the ollama service outputs
    """
    entrypoint_file = "/entrypoint.sh"
    terminate_processes("ollama")
     # Determine where to redirect the standard streams
    if log_file:
        # If a log file is provided, redirect stdout and stderr to the log file
        log_file_handle = open(log_file, "w")
        stdout = log_file_handle
        stderr = subprocess.STDOUT
    else:
        # If no log file is provided, redirect stdout and stderr to os.devnull (suppress output)
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL
    
    if os.path.exists(entrypoint_file):
        # Start /entrypoint.sh as a background process using /usr/bin/bash
        try:
            serve_process = subprocess.Popen(["/usr/bin/bash", entrypoint_file], stdout=stdout, stderr=stderr)
            #added this since it takes a bit to get ollama service running 
            time.sleep(3)
            print(f"Started {entrypoint_file} as a background process.")
            logger.info(f"INFO : Started {entrypoint_file} as a background process.")
        except Exception as e:
            print(f"Error: {e}")
            # Terminate the background process if it's still running
            if serve_process.poll() is None:
                serve_process.terminate()
            sys.exit(1)
    else:
        # Start ollama serve as a background process
        try:
            serve_process = subprocess.Popen(["ollama", "serve"], stdout=stdout, stderr=stderr)
            #added this since it takes a bit to get ollama service running
            print("Started ollama serve as a background process.")
            logger.info(f"INFO : {entrypoint_file} not existing so started ollama manually as a background process.")
        except Exception as e:
            print(f"Error: {e}")
            # Terminate the background process if it's still running
            if serve_process.poll() is None:
                serve_process.terminate()
            sys.exit(1)

def pull_ollama_model(model=DEFAULT_LLM ): 
    """
    Call model and test how long it takes to invoke
    model :  Name of the Model to pull
    """
    # Code block to measure time to load model
    start_time = time.time()
    # let us load the model
    logger.info(f"INFO: pulling {model} from Ollama library")
    os.system(f"ollama pull {model}")


    #check if we get a response from the model
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': 'Why is the sky blue?'}])
    if (response['done'] == True):
        logger.info('INFO: Model Response Obtained')
    print(response)


    # Calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"INFO: Model Loaded and response, Time required: {elapsed_time:.6f} seconds")

def initialize_llm_settings(model=DEFAULT_LLM, embed_model = "BAAI/bge-small-en-v1.5",base_url=os.environ["OLLAMA_BASE_URL"]):
    """
    Initializes and configures settings for the Ollama instance.
    """
    Settings.llm = Ollama(model=model, request_timeout=10000)
    Settings.llm.base_url = OLLAMA_BASE_URL
    Settings.embed_model = FastEmbedEmbedding(model_name=DEFAULT_EMBEDDING_MODEL)
    

