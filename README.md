# WealthE:  A selfhosted Wealth Educator GenAI application for Indian Capital Markets 

![](./assets/images/app-logo.png)
## Disclaimer ##
**IMPORTANT :** This is an example of a GenAI Application that serves as a wealth assistant on Indian Capital Markets. The objectives is to demonstrate how to build domain specific GenAI applications. This application should **NOT BE CONSTRUED OR USED AS ANY SORT OF FINANCIAL ADVISE**. ***NOR SHOULD*** the responses from this application used for any sort of investment trades or trade specific strategies or backtesting. The outcomes are unknown and there are no guarantees to it, if you do so.  

## Purpose ## 
  Organisations are increasingly seeking to build Large Language Models(LLM) applications for embodying organizational knowledge. However, due to data sensitivity and security concerns, such applications trained on internal knowledge bases cannot use API based provider ( e.g. OpenAI). The ability to use  powerful open Large language Models ( e.g. llama models from Meta) augmented with contextual datasets provide promising solutions. Yet,evaluating these applications remain a challenge. 

   With this application, we address some of these requirements in build Enterprise knowledge systems using GenAI with performance evaluations
   WealthE is a wealth educator on Indian Capital Markets that
  - uses a llama(8b) model augmented on a captital makets and finance education data using Retrieval Augmented Generation (RAG) ( see references for more details on RAG )
  - holds memory i.e. remembers the prior question asked before formulating the next answer
  - demonstrates LLMOps : Uses an evaluation Triad of Groundedness, Answer Relevance and Context Relevance to benchmarking LLM Performance ( see section the Triad for more on this topic)
  - provides a ChatGPT style "smart" interface with streaming output to reduce the latency perceptions
  - uses a vector database to save the knowledge base that is used to augment the context for the Q&A with the underlying LLM 

### An Example response contextualized for Indian Capital Markets

![](assets/images/GenAi-app-contextualization.png)

## The WealthE Application
  WealthE serves as a wealth education assitant answering queries in Q&A style using a contextualized LLM. The "context augmentation" is
  achieved through a finance varsity data ( see references ) on Indian Capital Markets. As seen below, the application holds memory 
  across conversations. For. e.g. "when the user types can you tell me more ?, it remembers the earlier response and elaborates the response.
  
  ![](./assets/images/GenAI-app-with-memory.png)
  

## LLMOPs : Evaluation of the Generative AI Application 
  We demonstrate LLMOps by evaluating the application on a set of evaluation prompts.You can find the prompts in the folder assets/data/questions. 
  You can add additional questions or modify the questions in this file, and re-run 3_session-evaluate-llm step and view the results in steps 4_app-run-evaluation-dashboard.
    ![](./assets/images/Trulens-dashboard.png)
  
  Finally, you can compare these evaluations with the earlier ones in mlflow using 5_session-save-evaluations-in-mlflow. Following 2 questions are already performed. 
  ```
    What is fundamental Analysis ? 
    What are tax implications for traders ?
  ```
  
  Below we see the evaluations persisted in MLflow in Cloudera Machine Learning. This helps us compare overtime the performance of the application for newer prompts.
    ![](./assets/images/Experiment.jpg)
  
  
  
  **Note** : Since human evaluations is time consuming, we use LLMs to perform the evaluations. This is resource and time intensive and hence you may need to carefully
  evaluate the questions you will use for LLM evaluations. Refer to reference section to understand more around Trulens, the LLM Evaluation framework used here. 
  
  
## The Tech Bits ##
### Runtime Pre-requisites: ##
The WealthE AMP has some essential pre-requisites to work:
- A Custom community runtime called Ollama Runtime has been created. This runtime must be added to your Runtime catalog to enable the application to work. See instructions for adding the runtime [here](https://github.com/cloudera/community-ml-runtimes/tree/main/ollama)
-  GPU enabled compute: 1 GPU compute  instance is required to run the application and host the llama model. Use this for running the chat application, if you are not using the AMP. 

## Folder Structure ##
```
├── 0_session-install-dependencies: File sets up  the python packages to be installed
├── 2_job-data-ingest : File does a Web crawl and data ingest  to create a localized dataset
├── 3_app_run_llm_eval : Sets up the Tru Lens evaluation of the RAG Application
├── 4_app-run-chat-bot:  Runs the Finance bot application
├── assets
  ├── data
      ├── Chromadb : Contains the vectorized representations of the dataset 
      ├── index : stores the indexes for LLM Evaluations
      ├── questions: Stores a text file with evaluation questions
      ├── raw : stores the raw dataset that is generated by the web scrapper during data ingest
  ├── images
├── chainlit.md : Kept blank, can be configured for the chat bot application.
```

### Technology Stack and Architecture ###
Some of key components used for building this application are as follows:
- Ollama : used primarily for setting up local / off-the-grid LLMs
- Llamaindex : Used for setting up interfaces with the LLM and the front end application
- Chromadb : Vector Database holds the financial context dataset that is used to augment the prompts to the LLM
- Trulens : Used for evaluation and benchmarking based on Context Relevance, Answer Relevance and Groundedness of response 
- Chainlit : Used for the user interface. 





## References ##
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/pdf/2005.11401)
- [Dataset - Zerodha Varsity](https://zerodha.com/varsity/): An open financial education varsity on Indian capital markets

### Evaluation Triad ## 
For Evaluation we use the RAG Triad of Metrics described by TruLens and DeepLearning.ai 
(Reference / Image Credits: [Trulens](https://www.trulens.org/trulens_eval/getting_started/core_concepts/rag_triad/))
![](./assets/images/RAGTriad.jpg)

### Metrics Explanation:
1. **Context Relevance**: Assesses the quality of retrieved context in relation to the user’s query.
2. **Groundedness**: Measures how well the RAG’s final response is supported by the retrieved context.
3. **Answer Relevance**: Evaluates the relevance of the RAG’s final response to the original user query.

## Attribution ##
- Image created using Free Adobe Image Generator