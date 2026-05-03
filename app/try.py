
import os

from langchain_cohere import ChatCohere

client = ChatCohere(
    model="command-r-plus-08-2024",
    timeout_seconds=60,
    cohere_api_key=os.getenv("COHERE_API_KEY"),
)

response = client.invoke("Explain the importance of fast language models")

print(response.content)