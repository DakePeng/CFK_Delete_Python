#Acquiring metrics for CFK owned files, as of 1/2024. 
#This code retrieve data on new sets of files according to the following criteria:
#"dead" (no explicit share, no share via link, no last edit)
#"non-carleton only" (explicitly shared/last edited by non-carleton account, no share via link)
import sys
#!!! include the path of python packages here if you are not using a local machine !!!
#!!! delete this line if you are on your own device !!!
sys.path.append('c:/users/pengd/appdata/local/packages/pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0/localcache/local-packages/python312/site-packages')

from googleapiclient.discovery import build
import datetime
import multiprocessing
from authentication import get_credentials
from query import make_query
from my_multiprocessing import divide_list
import datetime
import multiprocessing

#!!!check the following variables!!!
#the table where we are finding data from
project_id = 'carlfilekeeper-database';
recent_export = '09_23_cfk_export';
table_name = 'all_files';

address = project_id + '.' + recent_export + '.' + table_name

#!!!check the following variables!!!
#number of files deleted each time this program is run
num_files_per_query = '10000'
num_processes_running_simultaneously = 16 

'''
    make a SELECT query to the bigQuery database to get num_files_per_query files to lookup
    @return: an array of fileids to delete
'''
def get_files_to_check():
    query = ('SELECT id FROM `' + address + '`WHERE isParsed= "0" LIMIT ' + num_files_per_query)
    rows = make_query(query)
    fileids_to_delete = []
    for row in rows:
        fileids_to_delete.append(row.id)
    return fileids_to_delete

'''
    make an UPDATE query to the bigQuery database to set the field 'isParsed' 
    of each fileid in the list fileids to '1'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_parsed(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET isParsed = "1" WHERE id IN ' + idlist)
    make_query(query)

'''
    make an UPDATE query to the bigQuery database to set the field 'isParsed' 
    of each fileid in the list fileids to '1'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_parsed(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET isParsed = "1" WHERE id IN ' + idlist)
    make_query(query)

'''
    make an UPDATE query to the bigQuery database to set the field 'isSharedviaLink' 
    of each fileid in the list fileids to '1'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_shared_via_link(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET isSharedviaLink = "1" WHERE id IN ' + idlist)
    make_query(query)

'''
    make an UPDATE query to the bigQuery database to set the field 'isSharedviaLink' 
    of each fileid in the list fileids to '0'
    
    @fileids: a list of fileids(string)
'''
def mark_files_as_not_shared_via_link(fileids):
    idlist = "( \'" + "\', \'".join(fileids) + "\')"
    query = ('UPDATE ' + address + ' SET isSharedviaLink = "0" WHERE id IN ' + idlist)
    make_query(query)

'''
    checks if a file is shared via link    
    @service: a Google service object created by googleapiclient.discovery.build
    @fileid: an string of fileid of the file to delete
    @return: True if the file is shared via link. False if not.
'''
def is_shared_via_link(service, fileid):
    check_status = 'Checking file with id ' + str(fileid)
    try:
        file_metadata = service.files().get(fileId=fileid, fields="permissions").execute()
        shared_via_link_anyone = any(permission.get('type') == 'anyone' for permission in file_metadata.get('permissions', []))
        shared_via_link_carleton = any(permission.get('type') == 'domain' for permission in file_metadata.get('permissions', []))
        check_status += " ------ success."
        print(check_status)
        return shared_via_link_anyone or shared_via_link_carleton
    except Exception as error:
        check_status += " ------ failed. Error message: " + str(error)
        print(check_status, file=sys.stderr)
        return False
    
'''
    helper function for batch_get_share_status_multiprocessing
    checks files in a list and append them to two separate lists depending on their share status
    @service: a Google service object created by googleapiclient.discovery.build
    @fileids: a list of file ids of files to delete
    @fileids_shared_via_link: a list to store files shared via link
    @fileids_not_shared_via_link: a list to store files not shared via link
'''
def batch_get_share_status_multiprocessing_helper(service, fileids,fileids_shared_via_link, fileids_not_shared_via_link):
    for fileid in fileids:
        if(is_shared_via_link(service, fileid)):
            fileids_shared_via_link.append(fileid)
        else:
            fileids_not_shared_via_link.append(fileid)

'''
    use multuthreadding to check the sharing status of files
    @service: a Google service object created by googleapiclient.discovery.build
    @fileids: an array of file ids of files to check
'''
def batch_get_share_status_multiprocessing(fileids, service):
    chunks = divide_list(fileids, num_processes_running_simultaneously)
    processes = []
    fileids_shared_via_link = multiprocessing.Manager().list()
    fileids_not_shared_via_link = multiprocessing.Manager().list()
    # Create and start multiple processes
    for i in range(num_processes_running_simultaneously):
        process = multiprocessing.Process(target= batch_get_share_status_multiprocessing_helper, args=(service, chunks[i], 
                                            fileids_shared_via_link,fileids_not_shared_via_link))
        processes.append(process)
        process.start()
    
    # Wait for all processes to finish
    for process in processes:
        process.join()
        
    fileids_shared_via_link = [sublist for sublist in fileids_shared_via_link]
    fileids_not_shared_via_link = [sublist for sublist in fileids_not_shared_via_link]
    return (fileids_shared_via_link, fileids_not_shared_via_link)

if __name__ == '__main__':
    print("starting time: " + str(datetime.datetime.now()))
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    files_to_check = get_files_to_check()
    (fileids_shared_via_link, fileids_not_shared_via_link) = batch_get_share_status_multiprocessing(files_to_check, service)
    mark_files_as_parsed(files_to_check)
    mark_files_as_shared_via_link(fileids_shared_via_link)
    mark_files_as_not_shared_via_link(fileids_not_shared_via_link)
    print("end time: " + str(datetime.datetime.now()))