# CFK_Delete_Python
Deletion code for the CFK Project

# Prerequisites
To run this code, make sure you have installed:

Python 3
pip
[Google CLI] [https://www.bing.com/search?pglt=2083&q=google+cli&cvid=e7c054ae71cc40cfbaf7345ed9b7af0f&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQABhAMgYIAhAAGEAyBggDEC4YQDIGCAQQABhAMgYIBRAAGEAyBggGEAAYQDIGCAcQABhAMgYICBBFGDzSAQgyNjQ3ajBqMagCALACAA&FORM=ANNTA1&PC=U531]

And enabled Google Drive API in your Google Cloud Service Project (carletonfilekeeper-database)

Make sure you have a credentials file named "client_id.json" in the same folder as the python code.

[Create an OAuth 2.0 Client ID credential as a desktop App] [https://developers.google.com/drive/api/quickstart/python]

Before you start running, run the following commands in terminal:

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install --upgrade google-cloud-bigquery

# Configuration

Before running, look at each comment in CFKdelete_mainprocess.py and CFKdelete_subprocess.py that is surrounded by 3 exclamation marks ("!!!")

You might get an error that says "no module named "google"". If you are not running on a local machine, change the line "sys.path.append(...)" to append the address where your google packages are installed. This should be in a subdirectory of the folder where you installed Python.

In "CFKdelete_subprocess.py", verify these information:

project_id
recent_export
table_name 
num_files_per_query

In "CFKdelete_mainprocess.py", verify: 

num_times_to_run

# Authentication

Set num_files_per_query in "CFKdelete_subprocess.py" to 1 and test run "CFKdelete_subprocess.py". There should be an authentification window that pops up. Login as CFK and allow access to drive. This will create a "token.json" file in you folder.

# Running the code

You can set num_files_per_query in "CFKdelete_subprocess.py" to 1 and test run "CFKdelete_subprocess.py". If everything works out, you can set this to a larger number (0 ~ 30000) and run "CFKdelete_mainprocess.py"

# Deleting a large number of files

In 12/2023 we are attempting to delete 2 million files. To do this, we will set up this code to run on a machine in ITS overnight. We estimate that it will take 20 days to delete all files.