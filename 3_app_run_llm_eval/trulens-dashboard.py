# Run the Tru lens app
from trulens_eval import Tru
import os
print(f'The Trulens Dashboard can be accessed in the URL: \n  https://{os.getenv("CDSW_ENGINE_ID")}.{os.getenv("CDSW_DOMAIN")} ')
Tru().run_dashboard(port=os.getenv("CDSW_APP_PORT"), address="127.0.0.1", force = True)