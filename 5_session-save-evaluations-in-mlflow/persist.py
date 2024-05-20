# Run the Tru lens app
import os
from utils.configs import TRULENS_DB_PATH, DEFAULT_LLM,EVAL_DATA_DIR, LLM_EXPERIMENT_NAME
# For some WIERD Reason, the mlflow experiment needs to be set before the Trulens_eval package. Else the mlflow.set_experiment fails. (Vish :10.May, This issue almost killed me from frustration )
import mlflow
import math
mlflow.set_experiment(LLM_EXPERIMENT_NAME)

from trulens_eval import Tru
from utils.logging_config import get_logger
# from  utils.rag_helper import *
logger = get_logger(__name__)


def read_questions_from_file(filename):
    """
    Reads questions from a file and returns them as a list.
    """
    questions = []
    with open(filename, 'r') as file:
        for line in file:
            questions.append(line.strip())
    return questions


def log_metric_safely(metric_name, value, not_computed_value=-999.0, not_computed_tag=None):
    """
    Logs a metric value to MLflow, handling NaN values gracefully.

    Parameters:
    - metric_name: The name of the metric to log.
    - value: The value of the metric.
    - not_computed_value: The value to log if the metric value is NaN (default is -999.0).
    - not_computed_tag: An optional tag name to set in MLflow if the metric value is NaN.
    """
    if math.isnan(value):
        # Log a default value if NaN
        mlflow.log_metric(metric_name, not_computed_value)
        # Optionally set a tag indicating the value was not computed
        if not_computed_tag:
            mlflow.set_tag(f"{metric_name}_status", "not_computed")
    else:
        # Log the actual value if it's not NaN
        mlflow.log_metric(metric_name, round(value, 2))
        
def save_evaluations_in_mlflow (eval_questions, eval_df):
    """
    This functions persists the TRIAD metrics into the mlflow experiments
    """

    # Add a try catch block
    logger.info("INFO: Setting MLFlow Experiments")    
    # Evaluations are stored as a data frame by Tru Lens
    #mlflow.set_experiment(exp_name)
    logger.info("INFO: Setting MLFlow Experiments")      
    llm_model = os.environ.get("LLM", DEFAULT_LLM)
    for index,row in eval_df.iterrows():
      mlflow.start_run()
      mlflow.set_tag("model_name", llm_model)
      mlflow.log_param("eval_data", eval_questions)
      mlflow.log_param("app_id", index)
      # we use this method, because sometimes the previous Trulens computations generates NaN and we need to handle it gracefully
      log_metric_safely("context_relevance_with_cot_reasons", round(row["context_relevance_with_cot_reasons"],2))
      log_metric_safely("relevance", round(row["relevance"],2))
      log_metric_safely("groundedness_measure_with_cot_reasons", round(row["groundedness_measure_with_cot_reasons"],2))
      log_metric_safely("latency", row["latency"])
      mlflow.log_artifacts(EVAL_DATA_DIR, artifact_path="states")      
      mlflow.end_run()   
    logger.info("INFO: Finished persisting to MLFlow Experiments")   
  
def  main():

    database_url = f"sqlite:///{TRULENS_DB_PATH}/default.sqlite"
    llm_model=os.getenv("LLM", DEFAULT_LLM)
    tru = Tru(database_url=database_url)
    eval_df = tru.get_leaderboard(app_ids=[])
    #get the questions
    questions_file = os.path.join(EVAL_DATA_DIR, 'evaluation_questions.txt')
    eval_questions = read_questions_from_file(questions_file)
    save_evaluations_in_mlflow( eval_questions, eval_df)

if __name__ == "__main__":
    main()
