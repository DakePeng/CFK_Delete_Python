from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

project_id = 'carlfilekeeper-database';
recent_export = '09_23_cfk_export';
table_name = 'non_carleton_files';
address = project_id + '.' + recent_export + '.' + table_name
num_files_per_query = '500'

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_id.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def delete_files(service, fileids):
    for fileid in fileids:
        delete_file(service, fileid)

def delete_file(service, fileid):
    deletion_status = 'Deleting file with id ' + str(fileid)
    try:
        service.files().delete(fileId=fileid).execute()
        deletion_status += " ------ succeeded."
    except:
        deletion_status += " ------ failed."
    
    print(deletion_status)

def make_query(query):
    from google.cloud import bigquery
    client = bigquery.Client()
    query_job = client.query(query)  # API request
    return query_job.result()  # Waits for query to finish
    
def get_files_to_delete():
    query = ('SELECT id FROM `' + address + '`WHERE deleted= "0" LIMIT ' + num_files_per_query)
    rows = make_query(query)
    fileids_to_delete = []
    for row in rows:
        fileids_to_delete.append(row.id)
    return fileids_to_delete

def mark_files_as_deleted(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET deleted = "1" WHERE id IN ' + idlist)
    make_query(query)
    
def unmark_files_as_deleted(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET deleted = "0" WHERE id IN ' + idlist)
    make_query(query)
    
if __name__ == '__main__':
    import os.path
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    fileids_to_delete = get_files_to_delete()
    delete_files(fileids_to_delete, service)
    mark_files_as_deleted(fileids_to_delete)
    