''' 
    By Dake Peng, Carleton 25'. Reference from ChatGPT and Google Documentation.
    https://chat.openai.com/share/73df68d6-5637-465f-8041-2f497ec37d16
    https://developers.google.com/drive/api/guides/about-sdk
    functions relative to deleting a batch of files in Google Drive according to fileids stored in a bigQuery database.
'''

import sys
#!!! include the path of python packages here if you are not using a local machine !!!
#!!! delete this line if you are on your own device !!!
sys.path.append('c:/users/pengd/appdata/local/packages/pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0/localcache/local-packages/python312/site-packages')
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import sys

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

# !!! VERIFY these before production !!!
project_id = 'carlfilekeeper-database';
recent_export = '09_23_cfk_export';
table_name = 'non_carleton_files';
address = project_id + '.' + recent_export + '.' + table_name
num_files_per_query = '500'

'''
    Written by ChatGPT
    get Google credentials based on the local file "client_id.json"
    you can call Google service functions based on these credentials
    
    @return: cred, a google.oauth2.Credentials.credentials object
'''
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

'''
    delete multiple Google files based on their file id
    
    @service: a Google service object created by googleapiclient.discovery.build
    @fileids: an array of file ids of files to delete
'''
def delete_files(service, fileids):
    for fileid in fileids:
        delete_file(service, fileid)

'''
    delete one Google file based on its file id
    and prints the status of this deletion
    
    @service: a Google service object created by googleapiclient.discovery.build
    @fileid: an string of fileid of the file to delete
'''
def delete_file(service, fileid):
    deletion_status = 'Deleting file with id ' + str(fileid)
    try:
        service.files().delete(fileId=fileid).execute()
        deletion_status += " ------ succeeded."
        print(deletion_status)
    except Exception as error:
        deletion_status += " ------ failed. Error message: " + str(error)
        print(deletion_status, file=sys.stderr)
    

'''
    make a given query to the bigQuery database specified in the global variable "address"
    @query: a string of the SQL query to make
    
    @return: the result of the query
'''
def make_query(query):
    from google.cloud import bigquery
    client = bigquery.Client(project= "carlfilekeeper-database")
    query_job = client.query(query)  # API request
    return query_job.result()  # Waits for query to finish

'''
    make a SELECT query to the bigQuery database to get num_files_per_query files to delete
    
    @return: an array of fileids to delete
'''
def get_files_to_delete():
    query = ('SELECT id FROM `' + address + '`WHERE deleted= "0" LIMIT ' + num_files_per_query)
    rows = make_query(query)
    fileids_to_delete = []
    for row in rows:
        fileids_to_delete.append(row.id)
    return fileids_to_delete

'''
    make an UPDATE query to the bigQuery database to set the field 'deleted' 
    of each fileid in the list fileids to '1'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_deleted(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET deleted = "1" WHERE id IN ' + idlist)
    make_query(query)

'''
    make an UPDATE query to the bigQuery database to set the field 'deleted' 
    of each fileid in the list fileids to '0'
    
    @fileids: a list of fileids(string)
'''
def unmark_files_as_deleted(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET deleted = "0" WHERE id IN ' + idlist)
    make_query(query)

'''
    start a process that deletes num_files_per_query files in the bigQuery database
'''
if __name__ == '__main__':
    import os.path
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    fileids_to_delete = get_files_to_delete()
    '''
    delete_files(fileids_to_delete, service)
    mark_files_as_deleted(fileids_to_delete)
    '''
    