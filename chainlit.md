
# A self-hosted Wealth Educator GenAI application for Indian Capital Markets using Ollama and llama3 🚀🤖 

![](assets/images/app-logo.png)
## Purpose
WealthE is a wealth educator Assistant  that is contextualized to answer questions on Capital Markets in an Indian context. The bot holds memory of previous questions asked and also provides a evaluation framework to evaluate LLM responses. These evaluations are then stored in Cloudera Machine Learning MLOps framework for comparing prompt-response performance of the models. This Initial page will change after a few seconds

## Strong Disclaimer 
This assistant should be used for Education only and should be considered as any form of investment advise. Absolutely No Liability or Guarantees exist on any usage of the application.


**SHOUD NOT CONSTRUED AT ANY POINT AS FINANCIAL ADVISE**

## Tech Stack:
- *Large Language Model* : llama3
- User Interface : Chainlit
- Chat Framework : llamaIndex
- Evaluation Framework : Trulens
- vectordb : Chromadb

##  Example Questions toask : 
- What is the role of RBI ?
- Can you say more ? ( This should elaborate on the previous question)
- Who are some important regulators which we should know about?
- What are some taxation rules for stock trading?
- can you give some examples of Gilt funds?

## Credits 🔗
- [Retrieval Augmented Generation (RAG)](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf)
- Dataset : [Zerodha Varsity](https://zerodha.com/varsity/chapter-sitemap2.xml)