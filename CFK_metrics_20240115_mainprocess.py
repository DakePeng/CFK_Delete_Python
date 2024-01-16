''' 
    By Dake Peng, Carleton 25'.
    Acquiring metrics for CFK owned files, as of 1/2024. 
    This code retrieve data on new sets of files according to the following criteria:
    "dead" (no explicit share, no share via link, no last edit)
    "non-carleton only" (explicitly shared/last edited by non-carleton account, no share via link)
    !!! Check all comments surrounded by exclamation marks "!!!" before production. !!!
'''
import subprocess
from datetime import date
import os

#!!! verify this number (num_times_to_run) before production !!!
#number of times to run the subprocess
num_times_to_run = 250


'''
    Run subprocess and redirect output to a text file
'''
if __name__ == '__main__':
    date = date.today()
    error_file = str(date) + '_error_log.txt'
    with open(error_file, "w") as error_log:
        i = 0
        for j in range(num_times_to_run):
            #get today's date
            date = date.today()
            folder = str(date) + "_checkshared_log"
            if not os.path.exists(folder):
                i = 0
                os.makedirs(folder)
            output_file = "./" + folder + '/' + str(date) + '_attempt_' + str(i) + '_log.txt'
            with open(output_file, "w") as std_log:
                subprocess.run(["python", "CFK_metrics_20240115_subprocess.py"], stdout= std_log, stderr= error_log)
            i += 1

