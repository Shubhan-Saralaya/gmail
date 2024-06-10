import os.path
import base64
import email
import json
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

"""TODO 
  * GET EMAIL BY USER 
  * GET EMAIL ID TO REPLY
  * SEND EMAIL BODY TO OPENAI API
  * (CAN DO) RUN ON SERVER TO KEEP LOOKING FOR EMAILS FROM A CERTAIN USER
  """

def send_Email(service, recipent):
    emailReplyMsg = 'Just a test!'
    mimeReply = MIMEMultipart()
    mimeReply['to'] = recipent #! CHANGE TO RECIPIANT EMAIL
    mimeReply['subject'] = 'TEST1'
    mimeReply.attach(MIMEText(emailReplyMsg,'plain'))
    raw_string = base64.urlsafe_b64encode(mimeReply.as_bytes()).decode()
    message = service.users().messages().send(userId='me',body={'raw':raw_string}).execute()
    print(message)
    
    
def recieve_email(service):
    messagegot= service.users().messages().list(userId='me',maxResults=1).execute()
    for ID in messagegot.get("messages",[]):
      MimeMsg = email.message_from_bytes(base64.urlsafe_b64decode((service.users().messages().get(userId='me',id=ID['id'],format='raw').execute())['raw'].encode("ASCII")))
      print(MimeMsg)


def main():
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

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    #! recieve_email(service) (used to get email)
    #! send_Email(service, recipent) (used to send email)
    
  except HttpError as error:
  # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
  
  