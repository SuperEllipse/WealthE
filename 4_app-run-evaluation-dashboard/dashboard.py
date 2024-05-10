# Run the Tru lens app
import os
from utils.configs import TRULENS_DB_PATH
# For some WIERD Reason, the mlflow experiment needs to be set before the Trulens_eval package. Else the mlflow.set_experiment fails. (Vish :10.May, This issue almost killed me from frustration )

from trulens_eval import Tru
from utils.logging_config import get_logger
# from  utils.rag_helper import *
logger = get_logger(__name__)

def  main():

    print(f'The Trulens Dashboard can be accessed in the URL: \n  https://{os.getenv("CDSW_ENGINE_ID")}.{os.getenv("CDSW_DOMAIN")} ')
    database_url = f"sqlite:///{TRULENS_DB_PATH}/default.sqlite"
    Tru().run_dashboard(port=os.getenv("CDSW_APP_PORT"), address="127.0.0.1", force = True)
  
if __name__ == "__main__":
    main()
