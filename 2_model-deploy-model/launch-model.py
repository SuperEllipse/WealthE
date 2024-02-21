## Launch model python script

import cml.metrics_v1 as metrics
import cml.models_v1 as models

@models.cml_model(metrics=True)
def api_wrapper(args):
    return {"response": "response"}