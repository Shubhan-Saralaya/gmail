import os
import openai
from openai import AzureOpenAI


print(os.getenv("AZURE_OPENAI_ENDPOINT"))
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

def create_chat(body):
  response = client.chat.completions.create(
      model="probosys-demo", # model = "deployment_name".
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": body},

      ]
  )
  print(response.choices[0].message.content)
  return(response.choices[0].message.content)