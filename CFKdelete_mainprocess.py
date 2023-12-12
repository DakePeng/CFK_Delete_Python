''' 
By Dake Peng, Carleton 25'.
Main deletion program for the CFK project
'''
import subprocess
from datetime import date

num_times_to_run = 10
'''
    it takes roughly 5 minutes to complete each run that deletes 500 files. 
    this means if we leave the program running 14 consecutive days, it will be able to delete all 2 million files
    
    To be tested:
    Google has a quota of 12,000 requests per minute. That is the max # of deletions we can do with this code.
    https://developers.google.com/drive/api/guides/limits
'''

if __name__ == '__main__':
    for i in range(num_times_to_run):
    
        #get today's date
        date = date.today()
        
        # Run subprocess and redirect output to a text file
        output_file = str(date) + '_attempt_' + str(i) + '_log.txt'
        with open(output_file, "w") as file:
            subprocess.run(["python", "CFKdelete_subprocess.py"], stdout=file)