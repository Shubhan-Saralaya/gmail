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
          #{'role':"system","content":"you are a helpful AI Assistant"},
          {"role": "system", "content": "Review this invite and provide me with a scorecard.The scorecard should be on a scale of 1 to 5 for each of these items.Clarity of agenda, background information/read ahead material and Desired Outcome.Provide a score for each along with suggestions for improvement and also provide an Overall Score at the end. "},
          {"role": "user", "content": body},

      ]
  )
  print(response.choices[0].message.content)
  return(response.choices[0].message.content)