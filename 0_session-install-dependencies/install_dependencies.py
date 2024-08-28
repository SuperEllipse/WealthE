## This file is provided to the user to accelerate installing dependencies. 
## Look at sample implementations of this in practice as part of the AMP build script in sample-project-metadata/project-metadata-sample-1.yaml


import os
import sys
import time
import subprocess

# Let us check right upfront if Ollama Runtime is installed
try:
    result = subprocess.run(['ollama', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("OLLAMA Runtime found")
    if result.returncode != 0 and "/bin/bash: ollama: command not found" in result.stderr:
        raise Exception("The 'ollama' command is not installed or not found in the system PATH.")
    else:
        print(result.stdout)



except Exception as e:
    print(f"Error: {e}")
    print (f"You need to use a Runtime with ollama to make this application work. Have you chosen the right runtime ?")
    sys.exit(1)  # Exit with a non-zero status code


!pip install --upgrade pip
!pip install --no-cache-dir --log 0_session-install-dependencies/pip-req.log -r 0_session-install-dependencies/requirements.txt
