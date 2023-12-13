'''
    Run this code only when you manually interrupt the deletion process.
    The deletetion of files recorded in the the latest log would have happened, 
    but they are not updated on our database
    change the log_path to the latest log and hit run.
'''
from CFKdelete_subprocess import *

log_path = "./2023-12-13_log/2023-12-13_attempt_17_log.txt"
fileid_list = []
with open(log_path, "r") as file:
    for line in file:
        line_list = line.split()
        if(line_list[0] == 'Deleting'):
            id = line_list[4]
            fileid_list.append(id)

creds = get_credentials()
service = build('drive', 'v3', credentials=creds)
mark_files_as_deleted(fileid_list)