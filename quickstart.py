import os.path
from chat import create_chat
import base64
import email
import json
import time
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

timern= time.time()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

"""TODO 
  * GET EMAIL ID TO REPLY (Done)
  * KEEP LOOKING FOR EMAILS FROM A CERTAIN USER (Done- looking for any new unread emails)
  """
version = 3

def watch(service):
  messagegot=service.users().messages().list(userId='me',maxResults=5,q='is:unread').execute()
  #print(timern)
  if(len(messagegot)>1):
    for ID in messagegot.get("messages",[]):
      MimeMsg = email.message_from_bytes(base64.urlsafe_b64decode((service.users().messages().get(userId='me',id=ID['id'],format='raw').execute())['raw'].encode("ASCII")))
      for part in MimeMsg.walk():
        if part.get_content_type() == 'text/plain':
          body = part.get_payload(decode=True).decode('utf-8')
          print('#',body,'#')
          reply_body=create_chat(body)
          #print(reply_body)
      #MimeMsg = email.message_from_bytes(base64.urlsafe_b64decode((service.users().messages().get(userId='me',id=ID['id'],format='raw').execute())['raw'].encode("ASCII")))
      MimeMsg = service.users().messages().get(userId='me',id=ID['id'],format='full').execute()
      threadID = MimeMsg['threadId']
      
      references=None
      
      for part in MimeMsg['payload']['headers']:
        if(part['name']=='From'):
          To_address=part['value']
        if(part['name']=='Subject'):
          subject=part['value']
        if(part['name']=='Message-ID'):
          msg_Id=part['value']
        if(references==None):
          if(part['name']=='References'):
            references= part['value']
            print('set')
      reply_info={
        'body':reply_body,
        'message_Id':msg_Id,
        'threadID':threadID,
        'to':To_address,
        'references':references,
        'subject':subject
      }
      print(reply_info)
      if(mark_unread(service,ID)):
        send_Email(service,reply_info)
  else:
    time.sleep(2)
    
    
def mark_unread(service,ID):
  print(service.users().messages().modify(userId='me',id=ID['id'],body={'removeLabelIds':'UNREAD'}).execute())
  return True
  

def send_Email(service, reply_info):
    #print(reply_info)
    emailReplyMsg = reply_info['body']
    mimeReply = MIMEMultipart()
    mimeReply['to'] = reply_info['to'] #! CHANGE TO RECIPIANT EMAIL
    # mimeReply['From']='me'
    mimeReply['subject'] = reply_info['subject']
    mimeReply['threadId']=reply_info['threadID']
    mimeReply['in-reply-to']=reply_info['message_Id']
    if(reply_info['references']!=None):
      mimeReply['References']=reply_info['references']
    #mimeReply['to'] = 'saralayashubhan@gmail.com' #! CHANGE TO RECIPIANT EMAIL
    mimeReply['From']='me'
    #mimeReply['subject'] = 'testing3'
    #mimeReply['threadId']='1900e33c19ae1b21'
    #mimeReply['in-reply-to']='<CAMxsQxaARAAJrfQcqVcFWcpQUaO_2Y2vZ=cOXoaCFuSeyv3XHg@mail.gmail.com>'
    mimeReply.attach(MIMEText(emailReplyMsg,'plain'))
    raw_string = base64.urlsafe_b64encode(mimeReply.as_bytes()).decode()
    message = service.users().messages().send(userId='me',body={'raw':raw_string}).execute()
    print(message)
    

   
 
    
def recieve_email(service):
    messagegot= service.users().messages().list(userId='me',maxResults=1).execute()
    for ID in messagegot.get("messages",[]):
      MimeMsg = email.message_from_bytes(base64.urlsafe_b64decode((service.users().messages().get(userId='me',id=ID['id'],format='raw').execute())['raw'].encode("ASCII")))
      for part in MimeMsg.walk():
        if part.get_content_type() == 'text/plain':
          body = part.get_payload(decode=True).decode('utf-8')
          print(body)
        

def main():
  
  #-------------------------------------------- AUTH STUFF -------------------------------------------------------------------
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  #-------------------------------------------- AUTH STUFF -------------------------------------------------------------------

  try:
    # Call the Gmail API, use either function to recieve or send
    service = build("gmail", "v1", credentials=creds)
    x=0
    while x<30:
      watch(service)
      x+=1

  
  except HttpError as error:
  # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
  
  