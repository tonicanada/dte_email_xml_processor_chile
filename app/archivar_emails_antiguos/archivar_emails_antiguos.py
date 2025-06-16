from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import time

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
BATCH_SIZE = 1000
LOG_FILE = 'archivados.log'

def authenticate():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)

def archivar_batch(service, message_ids):
    if not message_ids:
        return
    service.users().messages().batchModify(
        userId='me',
        body={
            'ids': message_ids,
            'removeLabelIds': ['INBOX', 'UNREAD']
        }
    ).execute()
    print(f"Archivados y marcados como leídos: {len(message_ids)} mensajes")

    with open(LOG_FILE, 'a') as f:
        for msg_id in message_ids:
            f.write(f"{msg_id}\n")

def archivar_todos(service, query):
    all_ids = []
    next_page_token = None

    while True:
        response = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=next_page_token,
            maxResults=500
        ).execute()

        messages = response.get('messages', [])
        ids = [msg['id'] for msg in messages]
        all_ids.extend(ids)

        if 'nextPageToken' in response:
            next_page_token = response['nextPageToken']
        else:
            break

    print(f"Total mensajes encontrados: {len(all_ids)}")

    # Procesar en lotes
    for i in range(0, len(all_ids), BATCH_SIZE):
        batch = all_ids[i:i + BATCH_SIZE]
        archivar_batch(service, batch)
        time.sleep(0.5)  # Pausa ligera para evitar rate limits

if __name__ == '__main__':
    query = 'before:2025/06/01'
    gmail = authenticate()
    archivar_todos(gmail, query)
