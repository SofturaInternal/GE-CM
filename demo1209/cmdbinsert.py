import mysql.connector as mysql
import xlrd
import csv
import ConfigParser
import requests
import json
import pandas as pd
import sys
from requests.auth import HTTPBasicAuth
from mysql.connector import errorcode
import logging
import os
import errno
import datetime
now = datetime.datetime.now()
filename = now.strftime('logs/%Y/%m/%d/cmdbinsert.log')
#logname='git.log'
print(filename)
try:
        os.makedirs(os.path.dirname(filename))
except OSError as e:
        if e.errno != errno.EEXIST:
                print("Directory Exists!")
        else:
                print(str(e))

logname='cmdb.log'
logging.basicConfig(filename=filename,
                            filemode='a',
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%m/%d/%y %H:%M:%S',
                            level=logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)



Release_Branch_Name = sys.argv[1]
Repo_Latest_Commit_No = sys.argv[2]
Repo_Name = sys.argv[3]
Type = sys.argv[4]
if Type == "MD":
	Status = "Not Applicable"
else:
	Status = "Jenkins has started"
logging.info('The repo name is :')
logging.info(Repo_Name)


#########################
#Connectiong to Database#
#########################

logging.info("Connecting to the database")

try:
  db = mysql.connect(
	host = "localhost",
	user= "cmuser",
	password= "cmuser")
  logging.info("Connected to the mysql database 3.125.182.23")
except mysql.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    logging.error("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    logging.error("Database does not exist")
  else:
    logging.error(err)
  sys.exit(1)
  
logging.info("Connected to the database")

################################################################################
#executing the sql query which creates database and tables if not exists#
################################################################################

cursor = db.cursor(buffered=True)



def executeScriptsFromFile(cmdbdesign):
    fd = open(cmdbdesign, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        try:
            if command.strip() != '':
                cursor.execute(command)
        except IOError, msg:
            print "Command skipped: ", msg

#executeScriptsFromFile('cmdbdesign.sql')

#executeScriptsFromFile('insertscript.sql')



#############################
#Creating Audit log function#
#############################

logging.info("creating the audit log table")

def insert_log(msg , cursor = cursor , level = 'INFO'):
	sql = 'INSERT INTO cmdb_design.AuditLogs(`BuildNumber` , `ScriptName`, `LogLevel`, `LogMessage`) VALUES (%s, %s, %s, %s)'
	cursor.execute(sql, (Release_Branch_Name, ScriptName, level, msg))
	
ScriptName = 'cmdbinsert.py'

try:
	print os.path.basename(__file__)
	ScriptName = os.path.basename(__file__)
except Exception as e: 
	logging.error(e)
	insert_log(msg = str(e) , level = 'WARNING')

logging.info("Audit log table is created and values inserted")
insert_log(msg = "Audit log starts here")

####################
#Convert XLS -> CSV#
####################
'''
insert_log(msg = 'Converting XLS to CSV' )
wb = xlrd.open_workbook('QueryResult.xls')
sh = wb.sheet_by_name('IBM Rational ClearQuest Web')
your_csv_file = open('cmdb-defect.csv', 'wb')
wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
for rownum in xrange(sh.nrows):
  wr.writerow(sh.row_values(rownum))
your_csv_file.close()
logging.info("QueryResult xls file is converted to csv")
#logging.shutdown()
#print "xls file converted to csv" 
'''


#################################################################################
#Open the two csv files QueryResults.csv and config.csv from CQ values into CMDB#
#################################################################################

with open("cmdb-defect.csv") as f:
        read = csv.DictReader(f)
        data = [r for r in read]



#print('\n'.join(map(str, data)))




'''
def dict_gen(curs):
    
    import itertools
    field_names = [d[0].lower() for d in curs.description]
    while True:
        rows = curs.fetchmany()
        if not rows: return
        for row in rows:
            yield dict(itertools.izip(field_names, row))
'''
#property_list = [r for r in dict_gen(c.execute('select PropertyName , MAX(PropertyValue) , max(VersionNo) from cmdb_design.Properties GROUP BY PropertyName'))]

######################################################
#Get CMDB Properties from MySQL CMDB Properties Table#
######################################################
logging.info("Inserting the values into Properties table")
insert_log(msg = "Inserting the values into Properties table")

query_info = ("select PropertyName , MAX(PropertyValue) , max(VersionNo) from cmdb_design.Properties GROUP BY PropertyName")
cursor.execute(query_info)

property_list = list(cursor.fetchall())
for property in property_list:
	print property
property_df = pd.DataFrame(property_list)
property_df.columns = ['PropertyName', 'PropertyValue' , 'VersionNo']
Build_Machine = property_df[property_df.PropertyName == 'Build_Machine']["PropertyValue"].values[0]
Tollgate_URL = property_df[property_df.PropertyName == 'Tollgate_URL']["PropertyValue"].values[0]
Jenkinsfile_Commit_No = property_df[property_df.PropertyName == 'Jenkinsfile_Commit_No']["PropertyValue"].values[0]
Software_Tools = property_df[property_df.PropertyName == 'Software_Tools']["PropertyValue"].values[0]
Hardware_Platform = property_df[property_df.PropertyName == 'Hardware_Platform']["PropertyValue"].values[0]
Testing_Tools = property_df[property_df.PropertyName == 'Testing_Tools']["PropertyValue"].values[0]
BoM=property_df[property_df.PropertyName == 'BoM']["PropertyValue"].values[0]
			
logging.info("Values inserted into Properties table")
insert_log(msg = "Values inserted into Properties table")


#################################
#Getting Length of Repo Table#
#################################

logging.info("Getting the length of Repo table")
insert_log(msg = "Getting the length of Repo table")

def get_repo_length(cursor = cursor):
	query_info = ("select count(1) as count from cmdb_design.repo")
	cursor.execute(query_info)
	release_length = list(cursor.fetchall())
	release_df = pd.DataFrame(release_length)
	release_df.columns = ['count']
	release_count = release_df.loc[0,'count']
	return release_count

query_info = ("select count(1) as count from cmdb_design.release")
cursor.execute(query_info)
release_length = list(cursor.fetchall())
release_df = pd.DataFrame(release_length)
release_df.columns = ['count']
release_count = release_df.loc[0,'count']

##############y
#Main Function#
###############

logging.info("Entering into the Main function")
insert_log(msg = "Entering into the main function")

logging.info("Reading values from cmdb-defect.csv file")
insert_log(msg = "Reading values from cmdb-defect.csv file")

row = read.line_num - 1
#repo = 'gets-base'
repo = Repo_Name
j = release_count


logging.info("Inserting values into Repo Table")
insert_log(msg = "Inserting values into Repo Table")


k = get_repo_length()
print("THe repo length is ")
print(k)
for i in range(0,row):
    Product_Descriptor_Level3 = data[i]['Product_Descriptor_Level3']
    if Product_Descriptor_Level3 == repo:
       print(k)
       k = k+1
       id = data[i]['id']
       Product_Descriptors = data[i]['Product_Descriptors']
       VersionFixed = data[i]['VersionFixed']
       #ReleaseID = data[i]['ReleaseID']
       #Repo_ID = data[i]['Repo_ID']
       if "DateTime" in data [i]:
           DateTime = data[i]['DateTime']
       else:
           DateTime = None
       if "Version" in data[i]:
   	   Version = data[i]['Version']
       else: 
           Version = None
       if "SRP" in data[i]:
           SRP = data[i]['SRP']
       else: 
           SRP = None
       if "SCO" in data[i]:
   	   SCO = data[i]['SCO']
       else:
	   SCO = None
       if "Repo_URL" in data[i]:
           Repo_URL = data[i]['Repo_URL']
       else:
           Repo_URL = Repo_Name
       if "Commit_No" in data[i]:
           Commit_No = data[i]['Commit_No']
       else:
           Commit_No = None
       if "DTR" in data[i]:
           DTR = data[i]['DTR']
       else:
           DTR = None
       if "Version_Fixed_In" in data[i]:
           VersionFixed = data[i]['VersionFixed']
       else:
           VersionFixed = None 	
       print "Inserting into Repo table"
       query = "INSERT INTO cmdb_design.repo (ReleaseID, Repo_ID, Repo_URL, Status, DTR, VersionFixed) VALUES (%s, %s, %s, %s, %s, %s)"
       print(query) 
       values = (j,k,Repo_URL, Status , DTR, Repo_Latest_Commit_No)
       print(values)
       try:
         cursor.execute(query, values)
         logging.info("values inserted into the repo table")
         insert_log(msg = "values inserted into the repo table")
       except mysql.Error as err:
         logging.error("Failed to insert values into repo table")
         logging.error(err)
         insert_log(msg = str(err) , level = 'ERROR')
	 insert_log(msg = "Failed to insert the values into repo table")		 
         db.commit()
         cursor.close()
	 sys.exit(1)
         logging.info("values inserted into the database")
       break

	   
logging.info("Inserting values into Repo Commits Table")
insert_log(msg = "Inserting values into Repo Commits Table")


for i in range(0,row):
    Product_Descriptor_Level3 = data[i]['Product_Descriptor_Level3']
    if Product_Descriptor_Level3 == repo:
       if "Repo_URL" in data[i]:
           Repo_URL = data[i]['Repo_URL']
       else:
           Repo_URL = Repo_Name
       if "VersionFixed" in data[i]:
           VersionFixed = data[i]['VersionFixed']
       else:
           VersionFixed = "NA"
       print "Inserting into Repo Commits table"
       query = "INSERT INTO cmdb_design.repocommits (Repo_ID, Commit_No) VALUES (%s, %s)"
       print(query) 
       values = (Repo_URL, VersionFixed)
       print(values)
       try:
         cursor.execute(query, values)
         logging.info("values inserted into the repo commits table")
         insert_log(msg = "values inserted into the repo commits table")
		 
       except mysql.Error as err:
         logging.error("Failed to insert values into repo commits table")
	 logging.error(err)
	 insert_log(msg = str(err) , level = 'ERROR')
	 insert_log(msg = "Failed to insert the values into repo commits table")		 
         db.commit()
         cursor.close()
	 sys.exit(1)
       logging.info("values inserted into the database")
       insert_log(msg = "values inserted into the database")
       
#########################################################################
#Inserting the config.csv values into CMDB#
#########################################################################
insert_log(msg = "Audit log ends here fro the repo")
db.commit()
cursor.close()
print "All Done! Bye, for now."
