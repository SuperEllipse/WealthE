import subprocess
import os
import chainlit as cl
import logging
import sys
sys.path.append('/home/cdsw/utils')
import imp

import utils.logging_config
imp.reload(utils.logging_config)

from utils.logging_config import get_logger
# Get the shared logger
logger = get_logger(__name__)

# Log messages at different levels
#logger.debug("This is a debug message.")
logger.info("This is an informational message.")
chainlit_app_file = "6_app-run-chat-bot/Chat.py"


print(f"Access the chainlit application here:\n https://read-only-{os.environ['CDSW_ENGINE_ID']}.{os.environ['CDSW_DOMAIN']}")
os.system(f"chainlit run --host localhost --port $CDSW_READONLY_PORT {chainlit_app_file}")
