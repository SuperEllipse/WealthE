import subprocess
import os
import chainlit as cl
import logging
import sys
sys.path.append('/home/cdsw/utils')
import imp

import logging_config
imp.reload(logging_config)

from logging_config import get_logger
# Get the shared logger
logger = get_logger(__name__)

# Log messages at different levels
#logger.debug("This is a debug message.")
logger.info("This is an informational message.")
#logger.warning("This is a warning message.")
#logger.error("This is an error message.")
#logger.critical("This is a critical message.")



#chainlit_app_file = "~/scripts/Query.py"
chainlit_app_file = "~/scripts/Chat.py"


print(f"Access the chainlit application here:\n https://read-only-{os.environ['CDSW_ENGINE_ID']}.{os.environ['CDSW_DOMAIN']}")
os.system(f"chainlit run --host localhost --port $CDSW_READONLY_PORT {chainlit_app_file}")


#This is a way to test if OLLAMA is setup
#prompt = '\'{ \
#  "model": "gemma:2b", \
#  "prompt": "Why is the sky blue?" }\''
#print(prompt)
#full_prompt = f'curl http://localhost:8080/api/generate -d {prompt}'
#print(full_prompt)
#os.system(full_prompt)