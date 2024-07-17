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
import icalendar 

timern= time.time()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

"""TODO 

  * Reply to user name
  * Ways to keep program active/standby
  """
version = 3

def watch(service):
  
  #?gets unread message
  messagegot=service.users().messages().list(userId='me',maxResults=5,q='is:unread').execute() 
  #?if unread found
  if(len(messagegot)>1): 
    for ID in messagegot.get("messages",[]):
      
      email_body,threadID,subject = "","",""
      MimeMsg = email.message_from_bytes(base64.urlsafe_b64decode((service.users().messages().get(userId='me',id=ID['id'],format='raw').execute())['raw'].encode("ASCII")))
      
      #? getting invite content
      invite_body = get_invite(service,ID) 
      
      #? getting email body & subject
      for part in MimeMsg.walk(): 
        if part.get_content_type() == 'text/plain':
          email_body = part.get_payload(decode=True).decode('utf-8')
          
      MimeMsg = service.users().messages().get(userId='me',id=ID['id'],format='full').execute()
      
      threadID = MimeMsg['threadId']
      references=None 
      
      
      #? getting rest of the email body      
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
      
      body = invite_body + "\n" +email_body + subject
      
      #?getting reply from chat GPT 
      reply_body= create_chat(body)
          
      
      reply_info={
        'body':reply_body,
        'message_Id':msg_Id,
        'threadID':threadID,
        'to':To_address,
        'references':references,
        'subject':subject
      }
      if(mark_unread(service,ID)):
        send_Email(service,reply_info)
        print('email sent to ' + To_address)
  else:
    time.sleep(1)
    
#? getting calendar invite content
def cal_details(data):
  cal = icalendar.Calendar.from_ical(data)
  for component in cal.walk():
    if component.name == "VEVENT":
      invite_content = component.get("summary")+"\n"+component.get('description')+"\n Meeting Start time:" + \
      (component.get('dtstart').dt).strftime("%m/%d/%Y, %H:%M:%S")+"\n Meeting End time:" +  (component.get('dtend').dt).strftime("%m/%d/%Y, %H:%M:%S")
      print(invite_content)
      return invite_content
  else:
    print("error getting invite data")
    return "data"
    
#? getting calendar invite
def get_invite(service,ID):
  attachId = None
  MimeMsg = service.users().messages().get(userId='me',id=ID['id'],format='full').execute()
  parts = MimeMsg['payload']
  if('attachmentId' in parts['body']):
    attachId= parts['body']['attachmentId']
  else:
    for part in MimeMsg['payload'].get('parts', []):
      if 'filename' in part and part['filename'].endswith('.ics'):
        attachId= part['body']['attachmentId']
  if(attachId != None):
    data = (service.users().messages().attachments().get(userId='me',messageId=ID['id'],id=attachId).execute())['data'] 
    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
    return cal_details(file_data)
  else:
    return ("No invite attached")

#? marking file as read after sending    
def mark_unread(service,ID):
  service.users().messages().modify(userId='me',id=ID['id'],body={'removeLabelIds':'UNREAD'}).execute()
  return True
  
#? function to send music
def send_Email(service, reply_info):
    emailReplyMsg = reply_info['body']
    mimeReply = MIMEMultipart()
    mimeReply['to'] = reply_info['to'] 
    #*mimeReply['to']='saralayashubhan@gmail.com'
    mimeReply['subject'] = reply_info['subject']
    mimeReply['threadId']=reply_info['threadID']
    mimeReply['in-reply-to']=reply_info['message_Id']
    if(reply_info['references']!=None):
      mimeReply['References']=reply_info['references']
    mimeReply['From']='me'
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
    while 1:
      watch(service)

  
  except HttpError as error:
  # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
  
  