import subprocess
from datetime import date

date = date.today()
num_times_to_run = 10

for i in range(num_times_to_run):
    # Run subprocess and redirect output to a text file
    output_file = str(date) + '_attempt_' + str(i) + '_log.txt'
    with open(output_file, "w") as file:
        subprocess.run(["python", "CFKdelete_subprocess.py"], stdout=file)