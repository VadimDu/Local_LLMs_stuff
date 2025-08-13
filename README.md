# Local LLMs stuff
Code and notebooks for connecting and interacting with Local LLMs, agentic tool usage and RAG practices. The implementation will be done mostly with LangChain framework, and maybe others modules as well. The local server end point is LM-Studio for most cases. HuggingFace API and codebase will be used as well.

At the moment most of the notebooks and codebase in this repository is for practicing and educational purpose, not for production use.

__Below you will find a brief overview of the concepts and implementations from this repo__

## Build LLM agent with LangChain
__When to use the different agent types:__

Use `initialize_agent()` if:
* You're using LangChain < v0.1
* Need simple zero-shot agents without complex tools

Use `create_react_agent()` if:
* Your LLM doesn't support function calling
* You need explicit "Thought/Action" logging

Use `create_openai_tools_agent()` for:
* LM Studio/OpenAI-style APIs ✅
* Complex tool interactions ✅
* Built-in chat history ✅

__Additional difference between create_react_agent() vs. create_openai_tools_agent():__
* `create_react_agent()` natively support tools usage, it is explicitly defined in its PromptTemplate, but it DOES NOT support "chat-history" - for single prompts uses only
* `create_openai_tools_agent()` does not explicitly define tools usage in its ChatPromptTemplate, and this capability depends on the underlying model, but it DOES support "chat-history"


## What is RAG?

Retrieval-Augmented Generation (RAG) is an architecture that augments a foundation LLM with external, up-to-date knowledge via a retrieval step before generation. It decouples the LLM's static training data from dynamic, domain-specific information.

__Core Components (Local Setup):__

* Vector Database: Stores embeddings of external documents (e.g., ChromaDB, FAISS, Weaviate).
* Embedding Model: Converts text → dense vectors (e.g., all-MiniLM-L6-v2, BGE-small).
* Retriever: Queries the DB for top-k relevant passages via similarity search (e.g., cosine distance).
* LLM: Takes the retrieved context + user query → generates a grounded response.
