# test.py
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:14b", base_url="http://localhost:11434")

response = llm.invoke("say hello in one sentence")
print(response.content)