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
import os
import errno
import datetime
now = datetime.datetime.now()
filename1 = now.strftime('release.log')
#logname='git.log'
print(filename1)
try:
        os.makedirs(os.path.dirname(filename1))
except OSError as e:
        if e.errno != errno.EEXIST:
                print("Directory Exists!")
        else:
                print(str(e))
import logging
logging.basicConfig(filename=filename1,
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

Release_type = sys.argv[2]
#Repo_Name = sys.argv[3]

logging.info('The Release Branch name is  %s', Release_Branch_Name)
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
#insert_log(msg = "Connected to the Database")

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
	
ScriptName = 'release-insert.py'

try:
	print os.path.basename(__file__)
	ScriptName = os.path.basename(__file__)
except Exception as e: 
	logging.error(e)
	insert_log(msg = str(e) , level = 'WARNING')

logging.info("Audit log table is created and values inserted")
insert_log(msg = "Audit log starts here")

##############################################################################
#Open the two csv files QueryResults.csv and config.csv from CQ values into CMDB#
#################################################################################
if Release_type == 'defect':
	data = pd.read_excel('defectQueryResult.xls')
elif Release_type == 'scn':
	data = pd.read_excel('scnQueryResult.xls')
else:
	logging.error("no suitable Query Result")
	data = pd.DataFrame()

data.dropna(inplace=True, how = 'all')

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
logging.info("Reading the values from Properties table")
insert_log(msg = "Reading values from the Properties table")

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
			
insert_log(msg = "Values read from the Properties table")
logging.info("Values read from the Properties table")

#################################
#Getting Length of Release Table#
#################################

logging.info("Getting the length of Release Table")
insert_log(msg = "Getting the length of Release Table")

query_info = ("select count(1) as count from cmdb_design.release")
cursor.execute(query_info)

release_length = list(cursor.fetchall())
release_df = pd.DataFrame(release_length)
release_df.columns = ['count']
release_count = release_df.loc[0,'count']

print "the release count is "
print  release_count



###############
#Main Function#
###############

logging.info("Entering into the Main function")
insert_log(msg = "Entering into the main function")

logging.info("Reading values from cmdb-defect.csv file")
insert_log(msg = "Reading values from cmdb-defect.csv file")

row = len(data)
data.reset_index(inplace=True,drop=True)
data = data.to_dict(orient = 'index')
#repo = 'gets-base'
repo = 'Repo_Name'
j = release_count
for i in range(0,row):
   try:
        Product_Descriptor_Level3 = data[i]['Product_Descriptor_Level3']
   except:
        notes = data[i]['notes'].split(";")
        discriptor = notes[0]
        Product_Descriptor_Level3 = notes[1]
   if Product_Descriptor_Level3 != repo:
       
       j = j+1
       id = data[i]['id']
       try:
       	   Product_Descriptors = data[i]['Product_Descriptors']
       except:
	   notes = data[i]['notes'].split(';')
	   Product_Descriptors = notes[0]
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
           Repo_URL = None
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

############################################
#Inserting the config.csv values into CMDB#
############################################
       logging.info("Inserting the values into the release table")
       insert_log(msg = "Inserting the values into the release table")
       query = "INSERT INTO  cmdb_design.release(ReleaseID, SRP , Release_Branch_Name, Tollgate_URL, Build_Machine, Jenkinsfile_Commit_No, Software_Tools, Hardware_Platform, Testing_Tools, BoM, Release_type) VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s)"
       values = (j, SRP, Release_Branch_Name, Tollgate_URL, Build_Machine, Jenkinsfile_Commit_No, Software_Tools, Hardware_Platform, Testing_Tools, BoM , Release_type)
       print values
       try:
         cursor.execute(query, values)
	 logging.info("values inserted into the release table")
	 insert_log(msg = "Values inserted to the release table")
       except mysql.Error as err:
         print err
         logging.error("Failed to insert values into release table")
         insert_log(msg = str(err) , level = 'ERROR')
	 insert_log(msg = "Failed to insert the values into release table")		 
         db.commit()
         cursor.close()
         sys.exit(1)
       print "Values inserted into Release table"
       break
	   

       

#########################################################################
#Inserting the config.csv values into CMDB#
#########################################################################
insert_log(msg = "Audit log ends here")
db.commit()
cursor.close()
logging.shutdown()
print "All Done! Bye, for now."
