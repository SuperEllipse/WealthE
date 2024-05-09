# Run the Tru lens app
from trulens_eval import Tru
import os
from utils.configs import TRULENS_DB_PATH
print(f'The Trulens Dashboard can be accessed in the URL: \n  https://{os.getenv("CDSW_ENGINE_ID")}.{os.getenv("CDSW_DOMAIN")} ')
database_url = f"sqlite:///{TRULENS_DB_PATH}/default.sqlite"
Tru(database_url=database_url).run_dashboard(port=os.getenv("CDSW_APP_PORT"), address="127.0.0.1", force = True)