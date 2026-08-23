from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

#def get_llm(model_name: str) -> ChatOllama:
 #   return ChatOllama(model=model_name, temperature=0.2)

def get_llm(model_name: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_name,
        temperature=0
    )