import sys
import csv
import xlrd
import mysql.connector as mysql
import os
import re
import csv
import requests
import json
from requests.auth import HTTPBasicAuth
import logging 
import pandas as pd
import datetime 
import errno
import pickle



branch = raw_input('New Branch :')

Release_Branch_Name = branch


try:
	data = pd.read_excel('defectQueryResult.xls')
	data.dropna(inplace=True,how='all')
    	csvfile='defectQueryResult.xls'
	#data=pd.read_csv(csvfile)
	print("defect QueryResult file is present")
	run_command = 'python defectscript.py ' + branch + ''
	os.system(run_command)
	file_split=csvfile.split('.')
	print(file_split)
	new_csvfile='processed/' + file_split[0] + '-' + branch + '.' + file_split[1]
	print(new_csvfile)
	os.rename(csvfile, new_csvfile)
except Exception as e:
        print(str(e))
	print("defects query result file is not available")

try:
        data = pd.read_excel('scnQueryResult.xls')
	data.dropna(inplace=True,how='all')
	csvfile='scnQueryResult.xls'
	#data=pd.read_csv(csvfile)
	print("scn QueryResult file is present")
	run_command = 'python scnscript.py ' + branch + ''
	os.system(run_command)
	file_split=csvfile.split('.')
	print(file_split)
	new_filename1='processed/' + file_split[0] + '-' + branch + '.' + file_split[1]
	print(new_filename1)
	os.rename(csvfile, new_filename1)
except Exception as e:
	print(str(e))
        print("scn query result file is not available")
	
