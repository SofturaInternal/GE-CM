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
import datetime
logname='cmdb.log'
logging.basicConfig(filename=logname,
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
Repo_URL = sys.argv[2]
New_DTR = sys.argv[3]
New_Status = sys.argv[4]



#########################
#Connectiong to Database#
#########################

logging.info("Connecting to the database")

try:
  db = mysql.connect(
	host = "localhost",
	user= "cmuser",
	password= "cmuser",charset = 'utf8')
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

cursor = db.cursor(buffered=True)


#############################
#Creating Audit log function#
#############################

logging.info("creating the audit log table")

def insert_log(msg , cursor = cursor , level = 'INFO'):
	sql = 'INSERT INTO cmdb_design.AuditLogs(`BuildNumber` , `ScriptName`, `LogLevel`, `LogMessage`) VALUES (%s, %s, %s, %s)'
	cursor.execute(sql, (Release_Branch_Name, ScriptName, level, msg))
	
ScriptName = 'jenksinsupdate.py'

try:
	print os.path.basename(__file__)
	ScriptName = os.path.basename(__file__)
except Exception as e: 
	logging.error(e)
	insert_log(msg = str(e) , level = 'WARNING')

logging.info("Audit log table is created and values inserted")
insert_log(msg = "Audit log starts here")


#################################
#Getting Entry of Release Table#####
#################################

logging.info("Getting the Entry of Release table")


query_info = ("select MIN(ReleaseID), MIN(Release_Branch_Name) , MAX(Version) as Version from cmdb_design.release GROUP BY Release_Branch_Name HAVING Release_Branch_Name = '" + Release_Branch_Name + "'")
print(query_info)
cursor.execute(query_info)

property_list = list(cursor.fetchall())
for property in property_list:
	print property
property_df = pd.DataFrame(property_list)
property_df.columns = ['ReleaseID' , 'Release_Branch_Name'  , 'Version']
Selected_ReleaseID = property_df[property_df.Release_Branch_Name == Release_Branch_Name]["ReleaseID"].values[0]


#################################
#Getting Entry of Repo Table#####
#################################

logging.info("Inserting the values into Repo table")
insert_log(msg = "Inserting the values into Repo table")


query_info = ("select Repo_ID, ReleaseID , Repo_URL  , VersionFixed from cmdb_design.repo WHERE Repo_URL = '" + Repo_URL + "' and ReleaseID = " + str(Selected_ReleaseID))
print(query_info)
cursor.execute(query_info)

property_list = list(cursor.fetchall())
for property in property_list:
	print property
property_df = pd.DataFrame(property_list)
property_df.columns = ['Repo_ID', 'ReleaseID' , 'Repo_URL'  , 'VersionFixed']
#property_df.loc[0 , 'Repo_ID'] = property_df.loc[0 , 'Repo_ID'].encode('utf-8')
print(property_df)
Old_Repo_ID = property_df[property_df.Repo_URL == Repo_URL]["Repo_ID"].values[0]
Old_ReleaseID = property_df[property_df.Repo_URL == Repo_URL]["ReleaseID"].values[0]
Old_Repo_URL = property_df[property_df.Repo_URL == Repo_URL]["Repo_URL"].values[0]
Old_VersionFixed = property_df[property_df.Repo_URL == Repo_URL]["VersionFixed"].values[0]
#sys.exit(1)

logging.info("Values inserted into Repo table")
insert_log(msg = "Values inserted into Repo table")

##############y
#Main Function#
###############

logging.info("Entering into the Main function")
insert_log(msg = "Entering into the Main function")

print "Updating into Repo table"
query = "REPLACE INTO cmdb_design.repo (ReleaseID, Repo_ID, Repo_URL, Status, DTR, VersionFixed) VALUES (%s, %s, %s, %s, %s, %s)"
print(query) 
values = (Old_ReleaseID,Old_Repo_ID,Old_Repo_URL, New_Status , New_DTR, Old_VersionFixed)
print(values)
try:
    cursor.execute(query, values)
    logging.info("values inserted into the repo table")
    insert_log(msg = "values inserted into the repo table")
except mysql.Error as err:
    logging.error("Failed to insert values into repo table")
    logging.error(err)
    insert_log(msg = str(err) , level = 'ERROR')
    insert_log(msg = "Failed to insert the values into release table")		 
    db.commit()
    cursor.close()
    sys.exit(1)
logging.info("values inserted into the database")
insert_log(msg = "values inserted into the database")     

	   

       
#########################################################################
#Inserting the config.csv values into CMDB#
#########################################################################
insert_log(msg = "Audit log ends here")
db.commit()
cursor.close()
print "All Done! Bye, for now."
