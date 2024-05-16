## This file is provided to the user to accelerate installing dependencies. 
## Look at sample implementations of this in practice as part of the AMP build script in sample-project-metadata/project-metadata-sample-1.yaml

!pip install --upgrade pip
!pip install --no-cache-dir --log 0_session-install-dependencies/pip-req.log -r 0_session-install-dependencies/requirements.txt