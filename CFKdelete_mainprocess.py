''' 
    By Dake Peng, Carleton 25'.
    Main deletion program for the CFK project
    Runs "CFKdelete_subprocess.py", and creates a log file to record successful deletions of each file.
    creates a log to record all unsuccessful deletions each day.

    !!! Check all comments surrounded by exclamation marks "!!!" before production. !!!
'''
import subprocess
from datetime import date
import os
'''
    !!! verify this number (num_times_to_run) before production !!!
    it takes roughly 5 minutes to complete each run that deletes 500 files. 
    this means if we leave the program running 14 consecutive days, it will be able to delete all 2 million files
    
    To be tested:
    Google has a quota of 12,000 requests per minute. That is the max # of deletions we can do with this code.
    (this may not effect our code at all)
    https://developers.google.com/drive/api/guides/limits
'''
#number of times to run the subprocess
num_times_to_run = 10


'''
    Run subprocess and redirect output to a text file
'''
if __name__ == '__main__':
    error_file = str(date) + '_error_log.txt'
    with open(error_file, "w") as error_log:
        for i in range(num_times_to_run):
            #get today's date
            date = date.today()
            folder = str(date) + "_log"
            if not os.path.exists(folder):
                os.makedirs(folder)
            output_file = "./" + folder + str(date) + '_attempt_' + str(i) + '_log.txt'
            with open(output_file, "w") as std_log:
                #!!! fix "testsubprocess.py" before production !!!
                subprocess.run(["python", "CFKdelete_subprocess.py"], stdout= std_log, stderr= error_log)