import io
import re
import os
import sys
import datetime
import multiprocessing

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from authentication import get_credentials

# !!! Check these parameters before production!!! 

# the path to which to files are downloaded
download_path = './test-download/'

project_id = 'carlfilekeeper-database';
recent_export = '09_23_cfk_export';
table_name = 'non_carleton_files';
address = project_id + '.' + recent_export + '.' + table_name

#number of files deleted each time this program is run
num_files_per_query = '10000'


#a dictionary that mapps google workspace mime types to local; for example, google docs maps to microsoft word
dictionary_google_mime_type_to_local_mime_type = {
    'application/vnd.google-apps.document' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.google-apps.spreadsheet' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.google-apps.drawing': 'image/jpeg',
    'application/vnd.google-apps.script': 'application/vnd.google-apps.script+json',
    'application/vnd.google-apps.jam' : 'application/pdf',
}

#a dictionary that mapps google workspace mime types to local extension; for example, google docs maps to .docx
dictionary_google_mime_type_to_local_extension = {
    'application/vnd.google-apps.document' : '.docx',
    'application/vnd.google-apps.spreadsheet' : '.xlsx',
    'application/vnd.google-apps.presentation': '.pptx',
    'application/vnd.google-apps.drawing': '.jpg',
    'application/vnd.google-apps.script': '.json',
    'application/vnd.google-apps.jam' : '.pdf',
}

google_file_mime_types = list(dictionary_google_mime_type_to_local_mime_type)

'''
    Downloads a binary file in Google drive by its id
    
    @service: a Google service object created by googleapiclient.discovery.build
    @fileid: an string of fileid of the file to delete
    @file_name_google: the name of the file in google drive (this needs to be converted into a legal file name in windows)
    @return: True if the download succeeded, False if not
'''
def download_file_binary(service, fileid, file_name_google):
    log_message = "Downloading binary file with id " + fileid
    try:
        # download the file to bytesIO
        request = service.files().get_media(fileId=fileid)
        file_handler = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handler, request)
        done = False
        
        #wait until the download is completed
        while done is False:
            _, done = downloader.next_chunk()
            
        #make a folder that is named by the file's fileid
        file_folder_path = download_path + fileid + '/'
        if not os.path.exists(file_folder_path):
            os.makedirs(file_folder_path)
        file_path = file_folder_path + format_windows_filename(file_name_google)
        
        #store the file in the folder
        with open(file_path, 'wb') as file:
            file.write(file_handler.getvalue())
        log_message += " ------ succeeded."
        print(log_message)
        return True
    
    except HttpError as error:
        log_message += " ------ failed."
        print(log_message)
        print(f"An error occurred while downloading binary file {fileid}: {error}", file=sys.stderr)
    return False

'''
    Exports a Google Workspace file and downloads it locally.

    @service: a Google service object created by googleapiclient.discovery.build
    @fileid: an string of fileid of the file to delete
    @file_name_google: a string of the name of the file in google drive (this needs to be converted into a legal file name in windows)
    @file_google_mime_type: a string of the meme type of the google workspace file
    @return: True if the download succeeded, False if not
'''
def download_file_google(service, fileid, file_name_google, file_google_mime_type):
    log_message = "Downloading google file with id " + fileid
    try:
        file_local_mime_type = get_local_mime_type(file_google_mime_type)
        print(file_local_mime_type)
        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId = fileid, mimeType = file_local_mime_type)
        file_handler = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handler, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        file_folder_path = download_path + fileid +'/'
        if not os.path.exists(file_folder_path):
            os.makedirs(file_folder_path)
        file_path = file_folder_path + format_windows_filename(file_name_google) + get_local_extension(file_google_mime_type)
        with open(file_path, 'wb') as file:
            file.write(file_handler.getvalue())
        log_message += " ------ succeeded."
        print(log_message)
        return True

    except HttpError as error:
        log_message += " ------ failed."
        print(log_message)
        print(f"An error occurred while downloading google file {fileid}: {error}", file=sys.stderr)
        return False

'''
    written by ChatGPT
    formats a string into a proper file name into a proper filename in windows
    @input_str: a string to be formatted
    @return: formatted_str, a formatted string stripped of special characters and spaces
'''
def format_windows_filename(input_str, replacement_char='_'):
    # Define a regex pattern for characters not allowed in Windows file names
    illegal_chars = re.compile(r'[<>:"/\\|?*]')

    # Replace illegal characters with the specified replacement character
    formatted_str = re.sub(illegal_chars, replacement_char, input_str)

    # Remove leading and trailing spaces
    formatted_str = formatted_str.strip()

    # Ensure the file name is not empty after replacement
    if not formatted_str:
        formatted_str = replacement_char

    return formatted_str

'''
    returns the mime type that the download file should have given the type in Google.
    @file_google_mime_type: a string of the meme type of the google workspace file
'''
def get_local_mime_type(file_google_mime_type):
    return dictionary_google_mime_type_to_local_mime_type.get(file_google_mime_type)

'''
    returns the extension tha the local file should have given the type in Google.
    @file_google_mime_type: a string of the meme type of the google workspace file
'''
def get_local_extension(file_google_mime_type):
    return dictionary_google_mime_type_to_local_extension[file_google_mime_type]

'''
    checks if a google_mime_type is a google application that can be exported.
    @file_google_mime_type: a string of the meme type of the google workspace file
'''
def is_exportable_google_application(file_google_mime_type):
    return file_google_mime_type in google_file_mime_types

'''
    downloads files in fileids to local drive
    @service: a Google service object created by googleapiclient.discovery.build
    @fileid: an string of fileid of the file to delete
    @return: (download_successful_fileids, download_unsuccessful_fileids), 2 lists of ids of files that are successfully and unsuccessfully downloaded
'''
def download_files(service, fileids):
    download_successful_fileids = []
    download_unsuccessful_fileids = []
    for fileid in fileids:
        file_metadata = service.files().get(fileId=fileid).execute()
        file_google_mime_type = file_metadata['mimeType']
        file_name = file_metadata['name']
        if(is_exportable_google_application(file_google_mime_type)): 
            is_download_success = download_file_google(service, fileid, file_name, file_google_mime_type)
        else:
            is_download_success = download_file_binary(service, fileid, file_name)
        if is_download_success:
            download_successful_fileids.append(fileid)
        else: 
            download_unsuccessful_fileids.append(fileid)
    return (download_successful_fileids, download_unsuccessful_fileids)

'''
    make a SELECT query to the bigQuery database to get num_files_per_query files to download
    
    @return: an array of fileids to download
'''
def get_files_to_download():
    query = ('SELECT id FROM `' + address + '`WHERE downloaded= "0" LIMIT ' + num_files_per_query)
    rows = make_query(query)
    fileids_to_delete = []
    for row in rows:
        fileids_to_delete.append(row.id)
    return fileids_to_delete

'''
    make a given query to the bigQuery database specified in the global variable "address"
    @query: a string of the SQL query to make
    
    @return: the result of the query
'''
def make_query(query):
    log_message = "Making query: " + str(query)
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project= "carlfilekeeper-database")
        query_job = client.query(query)  # API request
        log_message += " ------ succeded"
        print(log_message)
        return query_job.result()  # Waits for query to finish
    except Exception as error:
        log_message += " ------ failed, error message: " + str(error)
        print(log_message)
        print(log_message, file = sys.stderr)


'''
    make an UPDATE query to the bigQuery database to set the field 'downloaded' 
    of each fileid in the list fileids to '1'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_downloaded(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET downloaded = "1" WHERE id IN ' + idlist)
    make_query(query)

'''
    make an UPDATE query to the bigQuery database to set the field 'downloaded' 
    of each fileid in the list fileids to '-1'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_download_unsuccessful(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET downloaded = "-1" WHERE id IN ' + idlist)
    make_query(query)


if __name__ == "__main__":
    print("starting time: " + str(datetime.datetime.now()))
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    test_fileids = []
    download_files(service, test_fileids)
    
    fileids_to_download = get_files_to_download()
    (download_successful_fileids, download_unsuccessful_fileids) = download_files(service, fileids_to_download)
    mark_files_as_downloaded(download_successful_fileids)
    mark_files_as_download_unsuccessful(download_unsuccessful_fileids)
    print("end time: " + str(datetime.datetime.now()))
