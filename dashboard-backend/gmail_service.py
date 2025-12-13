from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

class GmailService:
    def __init__(self, access_token: str):
        # Create credentials directly from the access token
        self.creds = Credentials(token=access_token)
        self.service = build('gmail', 'v1', credentials=self.creds)

    def fetch_recent_emails(self, max_results=20):
        try:
            # 1. Fetch INBOX messages
            results_inbox = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results // 2, # Split budget
                labelIds=['INBOX']
            ).execute()
            
            # 2. Fetch SPAM messages
            results_spam = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results // 2,
                labelIds=['SPAM']
            ).execute()
            
            messages_inbox = results_inbox.get('messages', [])
            messages_spam = results_spam.get('messages', [])
            all_messages = messages_inbox + messages_spam
            
            if not all_messages:
                return []

            email_data = []

            # Callback for batch processing
            def callback(request_id, response, exception):
                if exception:
                    print(f"Error fetching message {request_id}: {exception}")
                    return
                
                headers = response['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown)')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                snippet = response.get('snippet', '')
                
                # Determine folder based on labelIds in response
                labels = response.get('labelIds', [])
                folder = 'Spam' if 'SPAM' in labels else 'Inbox'

                email_data.append({
                    "id": response['id'],
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "snippet": snippet,
                    "status": "clean" if folder == 'Inbox' else "blocked", # Naive initial status for UI
                    "threat": "Marked as Spam by Google" if folder == 'Spam' else None,
                    "folder": folder
                })

            # 3. Create Batch Request
            batch = self.service.new_batch_http_request(callback=callback)
            
            for msg in all_messages:
                batch.add(self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='full'
                ))
            
            batch.execute()
            return email_data
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
