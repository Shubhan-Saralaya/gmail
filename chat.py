import os
import openai
from openai import AzureOpenAI


print(os.getenv("AZURE_OPENAI_ENDPOINT"))
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)



response = client.chat.completions.create(
    model="probosys-demo", # model = "deployment_name".
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the best places to visit in spain?"},
        
    ]
)

print(response.choices[0].message.content)