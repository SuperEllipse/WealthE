# Run the Tru lens app
from trulens_eval import Tru
import os
Tru().run_dashboard(port=os.getenv("CDSW_APP_PORT"), address="127.0.0.1", force = True)