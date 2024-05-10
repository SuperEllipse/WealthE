import os
import sys
import time
import subprocess
import psutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, load_index_from_storage, Settings
from IPython.display import Markdown, display
import chromadb
import ollama
import pandas as pd


# Adding project utilities DEBUG ONLY CAN BE REMOVED LATER

import importlib
import utils.configs
importlib.reload(utils.configs)

sys.path.append("/home/cdsw/utils")
from utils.logging_config import get_logger
from  utils.rag_helper import *
logger = get_logger(__name__)

# Get the shared logger
from utils.logging_config import get_logger
logger = get_logger(__name__)
from utils.configs import (
    BASE_DIR, DATA_DIR, EVAL_DATA_DIR, RAW_DATA_DIR, 
    INDEX_DIR, DB_DIR, VECTORDB_COLLECTION, IMAGE_DIR,
    OLLAMA_BASE_URL, DEFAULT_LLM ,TRULENS_DB_PATH,TRULENS_DB_URL,
    LLM_EXPERIMENT_NAME,

)
#Evaluation Specific imports
from trulens_eval import TruLlama
from trulens_eval import Tru, Feedback, Select
from trulens_eval.feedback.provider.litellm import LiteLLM
from trulens_eval.app import App
from trulens_eval.feedback import Groundedness
# we initialise the Tru object as a global object
# A small trick to ensure that the default database is persisted in the right directory
#os.chdir(TRULENS_DB_PATH)
tru = Tru(database_url=TRULENS_DB_URL)
tru.reset_database()
#Change the db back to base directory This trick is only to make sure trulens database is created in the right directory
#os.chdir(BASE_DIR)

from utils.llm_helper import (
  is_process_running,
  validate_runtime,
  start_ollama_service, 
  pull_ollama_model,
  initialize_llm_settings,
  )

#define the model we will use 
llm_model = os.environ.get("LLM", DEFAULT_LLM)
logger.info(f"INFO: Selected model is {llm_model}")

def setup_vector_index():
    """
    Sets up the vector store and index for querying.
    IMPORTANT: Make sure the bootstrap is run first. 
    """
    db2 = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db2.get_or_create_collection(VECTORDB_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    logger.info("INFO: Loading the Index")
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

def execute_query(query_engine, query):
    """
    Executes a query using the specified query engine and prints the response.
    Potential response modes to play with are refine, compact, tree_summarize, simple_summarize, accumulate
    More details are here : https://docs.llamaindex.ai/en/stable/module_guides/deploying/query_engine/response_modes/
    """
    response = query_engine.query(query)
    print(response)

def load_documents(directory):
    """
    Load documents from the specified directory.
    """
    logger.info("INFO: Loading the documents")
    return SimpleDirectoryReader(directory).load_data()
  
  
def setup_feedback_system(query_engine, eval_llm_model="llama2"):
    """
    Sets up feedback mechanisms using Trulens and LiteLLM providers.
    
    Inputs:
    
    query_engine( Llamaindex query_engine Interface): Takes the query engine to be used for setting up feedbacks
    eval_mode: Evaluation model name that will be used here defaults to llam2
    app(string): Name of the LLM Application. This will be later used leader board
    
    Returns:
    Feedbackhooks
    
    """

    
    provider = LiteLLM()
   # provider.model_engine = "ollama/llama2"
    provider.model_engine = f"ollama/{llm_model}"
    provider.completion_args = {"api_base": OLLAMA_BASE_URL}
    
    context = App.select_context(query_engine)
    groundedness_provider = LiteLLM()
    groundedness_provider.model_engine = f"ollama/{llm_model}"
    #groundedness_provider.model_engine = f"ollama/gemma:2b"
    groundedness_provider.completion_args = {"api_base": os.environ["OLLAMA_BASE_URL"]}
    
    grounded = Groundedness(groundedness_provider=groundedness_provider)
    logger.info("INFO: Setting up feedback loops")
    # Define feedback functions
    f_groundedness = (
        Feedback(grounded.groundedness_measure_with_cot_reasons)
        .on(context.collect())  # collect context chunks into a list
        .on_output()
        .aggregate(grounded.grounded_statements_aggregator)
    )
    
    f_answer_relevance = (
        Feedback(provider.relevance)
        .on_input_output()
    )
    
    f_context_relevance = (
        Feedback(provider.context_relevance_with_cot_reasons)
        .on_input()
        .on(context)
        .aggregate(np.mean)
    )
    
    feedbacks = [f_groundedness, f_answer_relevance, f_context_relevance]
    return feedbacks

def read_questions_from_file(filename):
    """
    Reads questions from a file and returns them as a list.
    """
    questions = []
    with open(filename, 'r') as file:
        for line in file:
            questions.append(line.strip())
    return questions
  

# go through a list of questions for a baseline

def run_evals(eval_questions, tru_recorder, query_engine):
    """
    Runs evaluation based on a set of questions against a type of query engine
    Inputs:
    eval_questions(list) : List of evaluation questions
    tru_recorder(Trulens Recorder object)
    query_engine(Lllama Index Query Engine Interface)
    
    Returns:
      Nothing
    """
    for question in eval_questions:
        with tru_recorder as recording:
            response = query_engine.query(question)

def get_records_and_tru_feedback(app="Baseline"):
    """
    Queries the Tru() database to get the feedback and the original records used for evaluation of the RAG Application
    """
    records, feedback = tru.get_records_and_feedback(app_ids=[app])
    pd.set_option("display.max_colwidth", None)
  #  records[["input", "output"] + feedback]
    return records[["input", "output"] + feedback]


def run_rag_evaluations():
    """
    We run 3 different type of Indexes and use our RAG Triad to measure performance against different ways of Prompting the LLMs
    Baseline: Run against a Simple llama Index VectorIndex uses Simple sentence parser
    SentenceWindow: use window size to enhance the prompt context sent to LLM
    Auto Merge: Merge Different node sizes for enhanced prompting
    
    # Evaluation Details
    1. Trulens to evaluate the prompts on TRIAD : Groundedness, Relevance, CoT
    2. Mlflow experiment to log our experiment results

    """
    logger.info("INFO: running RAG Evaluations")    
    
    #Change the eval_llm_model name to llama2 or anything else you want.
    eval_llm_model = DEFAULT_LLM
    pull_ollama_model(model=eval_llm_model)  
    
    #load the documents to be used by the RAG
    documents =load_documents(directory=RAW_DATA_DIR)
    
    
    # Let us start with Baseline evalations
      # The evaluation data we will use    
    questions_file = os.path.join(EVAL_DATA_DIR, 'evaluation_questions.txt')
    eval_questions = read_questions_from_file(questions_file)
    display(eval_questions)
    #Run Baseline
    logger.info("INFO: Starting Baseline Evaluations") 
    baseline_query_engine = setup_vector_index().as_query_engine()  

    #first setup the feedback systems
    feedbacks = setup_feedback_system(baseline_query_engine)
    
    tru_recorder_baseline = get_prebuilt_trulens_recorder(
                              baseline_query_engine,
                              app_id ="Baseline", feedbacks=feedbacks)

    run_evals(eval_questions, tru_recorder_baseline, baseline_query_engine)
    display(get_records_and_tru_feedback("Baseline"))
    df = tru.get_leaderboard(app_ids=[])   
    logger.info("INFO: Ran Baseline Evaluations") 
    logger.info(f"LEADER BOARD: \n {df}")

    #Run Sentence Window Indexer of window size 1    
    # Let us go through these guestions now for sentencewindowNode Parser
    logger.info("INFO: Starting SentenceWindowsize 1 Evaluations") 
    sentence_window_index_1 = build_sentence_window_index(documents, save_dir=os.path.join(INDEX_DIR,"sentence_index1"), window_size=1)
    sentence_window_engine_1 = get_sentence_window_query_engine( sentence_window_index_1)
    tru_recorder_baseline = get_prebuilt_trulens_recorder(
                              sentence_window_engine_1,
                              app_id ='sentence windowsize 1', feedbacks=feedbacks)

    run_evals(eval_questions, tru_recorder_baseline, sentence_window_engine_1)
    df=tru.get_leaderboard(app_ids=[])
    logger.info("INFO: Ran Sentence Window size 1 Evaluations") 
    logger.info(f"LEADER BOARD: \n {df}")
        
    # let us go through a window size of 3
    logger.info("INFO: Starting SentenceWindowsize 3 Evaluations") 
    sentence_window_index_3 = build_sentence_window_index(documents, save_dir=os.path.join(INDEX_DIR,"sentence_index3"), window_size=3)
    sentence_window_engine_3 = get_sentence_window_query_engine( sentence_window_index_3)
    tru_recorder_3 = get_prebuilt_trulens_recorder(
                              sentence_window_engine_3,
                              app_id ='sentence windowsize 3', feedbacks=feedbacks)
    
    run_evals(eval_questions, tru_recorder_3, sentence_window_engine_3)
    df=tru.get_leaderboard(app_ids=[])
    logger.info("INFO: Ran Sentence Window size 3 Evaluations") 
    logger.info(f"LEADER BOARD: \n {df}")
    
    logger.info("INFO: Starting Merging Index(2048, 512)  Evaluations") 

    auto_merging_index_0 = build_automerging_index(documents,save_dir=os.path.join(INDEX_DIR, "merging_index_0"), chunk_sizes=[2048,512],
    )

    auto_merging_engine_0 = get_automerging_query_engine(
        auto_merging_index_0,
        similarity_top_k=12,
        rerank_top_n=6,
    )


    tru_recorder_AM_1 = get_prebuilt_trulens_recorder(
        auto_merging_engine_0,
        app_id ='Merging Index (chunksize:2048 & 512)', feedbacks=feedbacks
    )

    run_evals(eval_questions, tru_recorder_AM_1, auto_merging_engine_0)

    # run Evals
    df=tru.get_leaderboard(app_ids=[])
    logger.info("INFO: Ran Merging Index(2048, 512)  Evaluations") 
    logger.info(f"LEADER BOARD: \n {df}")


    #Now using 3 Layers of Automerging
    auto_merging_index_1 = build_automerging_index(
        documents,
        save_dir=os.path.join(INDEX_DIR,"merging_index_1"),
        chunk_sizes=[2048,512,128],
    )

    auto_merging_engine_1 = get_automerging_query_engine(
        auto_merging_index_1,
        similarity_top_k=12,
        rerank_top_n=6,
    )
    logger.info("INFO: Starting Merging Index( 2048,512,128)  Evaluations") 
    tru_recorder_AM_2 = get_prebuilt_trulens_recorder(
        auto_merging_engine_1,
        app_id ='Merging Index(chunksize: 2048,512,128)', feedbacks=feedbacks
    )

    run_evals(eval_questions, tru_recorder_AM_2, auto_merging_engine_1)

    df=tru.get_leaderboard(app_ids=[])  
    df=tru.get_leaderboard(app_ids=[])
    logger.info("INFO: Ran Merging Index(chunksize: 2048,512,128)  Evaluations") 
    logger.info(f"LEADER BOARD: \n {df}")
  
    logger.info("INFO: Starting persistence to MLFlow") 
    save_evaluations_in_mlflow(LLM_EXPERIMENT_NAME, eval_questions)
   
def save_evaluations_in_mlflow (exp_name, eval_questions):
    """
    This functions persists the TRIAD metrics into the mlflow experiments
    """
    import mlflow
    # Add a try catch block
    logger.info("INFO: Setting MLFlow Experiments")    
    # Evaluations are stored as a data frame by Tru Lens
    mlflow.set_experiment(exp_name)
    logger.info("INFO: Setting MLFlow Experiments")      
    df = tru.get_leaderboard(app_ids=[])
    for index,row in df.iterrows():
      mlflow.start_run()
      mlflow.set_tag("model_name", llm_model)
      mlflow.log_param("eval_data", eval_questions)
      mlflow.log_param("app_id", index)
      mlflow.log_metric("context_relevance_with_cot_reasons", round(row["context_relevance_with_cot_reasons"],2))
      mlflow.log_metric("relevance", round(row["relevance"],2))
      mlflow.log_metric("groundedness_measure_with_cot_reasons", round(row["groundedness_measure_with_cot_reasons"],2))
      mlflow.log_metric("latency", row["latency"])
      mlflow.end_run()   
    logger.info("INFO: Finished persisting to MLFlow Experiments")    
  
def  main():

    
    #validate the right runtime is selected
    validate_runtime()
    # Check if the 'ollama' process is already running

    if is_process_running('ollama'):
        logger.info(f"'INFO: ollama' is already running in background.")
    else:
        start_ollama_service()
    
    # Test a model, llama2 is also the default, so works without parameters
    pull_ollama_model(model=llm_model)  

    # initialize llama-index settings
    initialize_llm_settings(model=llm_model)
    # We check here if ollama is set up and it executes fine with basic generation
    query_engine = setup_vector_index().as_query_engine(response_mode="compact")    
    execute_query(query_engine, "What is SEBI and what are its responsibilities?")

    # Let us run our Rag Evaluations
    run_rag_evaluations()
    
    
  
if __name__ == "__main__":
    main()


