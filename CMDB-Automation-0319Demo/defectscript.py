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
now = datetime.datetime.now()
filename = now.strftime('logs/%Y/%m/%d/commit.log')
#logname='git.log'
print(filename)
try:
	os.makedirs(os.path.dirname(filename))
except OSError as e:
	if e.errno != errno.EEXIST:
		print("Directory Exists!")
	else:
		print(str(e))
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
Release_type='defect'
branch = Release_Branch_Name							
###########################################
#Initializing repo_dict and projectid_dict#
###########################################


repo_dict = {}

logging.info("Trying to read repo build types")
try:
	#Reading file
	with open('repo_list.pkl', 'rb') as f:
        	repo_dict = pickle.load(f)
except Exception as e:
	print(str(e))
	

projectid_dict = {}

logging.info("Trying to read project id names")
try:
	#Reading file
	with open('projectid.pkl', 'rb') as f:
        	projectid_dict = pickle.load(f)
except Exception as e:
	print(str(e))
	
							
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



############################################
#Regular Expressions for Magic Draw and GIT#
############################################

logging.info("Checking the regular expressions for MD and GIT")

magicdraw_expressions = [r'(?i)md' , "^\D*\d{4}\D*$" , r'(?i)magic' , '(?i)system' , '(?i)draw']

magicdraw_list = []
for magic_regex in magicdraw_expressions:
    magicdraw_list.append(re.compile(magic_regex))


	
git_expressions = ['(?i)git' , '(?i)pull' , r'\b[0-9a-f]{40}\b']

git_list = []
for git_regex in git_expressions:
    git_list.append(re.compile(git_regex))

logging.info("Verified regular expressions for MD and GIT")


###########################################
#Get latest commit number of develop branch
###########################################

logging.info("Getting the greatest commit from the multiple commits")


def GetCommit(org,repo , commit):
	try:
		url = 'https://github.build.ge.com/api/v3/repos/'+org+'/'+repo+'/commits/'+commit
		logging.info("The URL is %s" , url)
		logging.info("The Repo Name is %s" , repo)
		logging.info("The Commit Number is %s" , commit)
		headers = {'Authorization': 'token 6df8e6858e395acff14f29cbecf976e3eeec2650', 'content-type': 'application/json'}
		response = requests.get(url,headers=headers)
		if response.status_code==200:
			logging.info("Got the greatest commit number from the multiple commits for %s" %(repo))
		else:
			logging.error("Something is wrong with the repo name, verify it: %s" %(repo))
			sys.exit(1)
		jsonres = response.json()
		#print jsonres
		commitdate = jsonres["commit"]["author"]["date"]
		logging.info("commit date for %s" %(repo))
		#sys.exit(1)										
		#sha = jsonres['object']['sha']
		return commitdate
	except Exception as e:
		logging.info("Exception Occurred")
		logging.error('Error Message for Getting Commit is %s' , str(e))
		sys.exit(1)

 

########################
#Verify Repo type#
#######################
def checkserviceBuild(org,repo):
        url = 'https://github.build.ge.com/raw/'+org+'/'+repo+'/master/Jenkinsfile'
        headers = {'Authorization': 'token 6df8e6858e395acff14f29cbecf976e3eeec2650', 'content-type': 'application/json'}
        response = requests.get(url,headers=headers)
        if response.status_code==200:
           print("Got the latest commit number from the develop branch for ")
        else:
           print("Something is wrong with the repo name, verify it")

        print("Reading the contents of jenkins")
        jenkinsfile_text = response.text

        if "serviceBuild" in jenkinsfile_text:
                return 'serviceBuild'
        elif "cotsBuild" in jenkinsfile_text:
                return 'cotsBuild'
        elif "libraryBuild" in jenkinsfile_text:
                return 'libraryBuild'
        elif "dockerImage" in jenkinsfile_text:
		return 'dockerImage'
        else:
                return 'Unknown'

########################
#Create a release branch
########################

logging.info("defining the function to create the release branch")

def CreateBranch(org,repo,branch,version):
 try:
     url = 'https://github.build.ge.com/api/v3/repos/'+org+'/'+repo+'/git/refs'
     logging.info("The URL is %s" , url)
     logging.info("The Repo Name is %s" , repo)
     logging.info("The Commit Number is %s" , version)
     payload = {
     "ref": "refs/heads/" + branch,
     "sha": version
     }
     print("Getting Commit No.")
     headers = {'Authorization': 'token 6df8e6858e395acff14f29cbecf976e3eeec2650', 'content-type': 'application/json'}
     r = requests.post(url, data=json.dumps(payload), headers=headers)
     print str(r)
     return r
 except Exception as e:
	 logging.error('Error Message for CreateBranch is %s' , str(e))
	 sys.exit(1)

data = pd.read_excel('defectQueryResult.xls')
data.dropna(inplace=True , how = 'all')
#row = reader.line_num - 1




##########################
#Create a pre-release tag
##########################

logging.info("defining the function to create the pre-release tag")


def CreateTag(org,repo,version,tagname,description):
 try:
     url = 'https://github.build.ge.com/api/v3/repos/'+org+'/'+repo+'/releases'
     logging.info("The URL is %s" , url)
     logging.info("The Repo Name is %s" , repo)
     logging.info("The Commit Number is %s" , version)
     payload = {
     "tag_name": tagname,
     "target_commitish": version,
     "name": tagname,
     "body": description,
     "draft": False,
     "prerelease": True
     }
     headers = {'Authorization': 'token 6df8e6858e395acff14f29cbecf976e3eeec2650', 'content-type': 'application/json'}
     r = requests.post(url, data=json.dumps(payload), headers=headers)
     if r.status_code==201:
        logging.info("Pre-release Tag is created for %s" %(repo))
     elif r.status_code==422:
        logging.warn("Pre-release Tag is already created for %s" %(repo))
     else:
        logging.error("Failed to create the Pre-release Tag verify repo name: %s" %(repo))
        sys.exit(1)
 except Exception as e:
	 logging.error('Error Message for CreateTag is %s' , str(e))
	 sys.exit(1)

##########################
#Create a Tag in MagicDraw
##########################

logging.info("Defining the function to create the Tag in MD")

def MagicDraw(project_id,tag_name,tag_description,version):
 try:
     url = 'https://3.125.182.25:8111/osmc/resources/'+project_id+'/tags'
     logging.info("The URL is %s" , url)
     logging.info("The Project ID is %s" , project_id)
     logging.info("The Commit Number is %s" , version)
     payload = {
     "@type": ["ldp:DirectContainer", "kerml:Tag"],
     "dcterms:title": tag_name,
     "dcterms:description": tag_description,
     "commitID": version,
     "@context": "http://3.125.182.117:8111/osmc/schemas/tag"
     }
     headers = {'accept':'application/ld+json', 'content-type': 'application/ld+json'}
     r = requests.post(url, data=json.dumps(payload), headers=headers,auth=HTTPBasicAuth('503135589','Letmein!234'),verify=False)
     if r.status_code==201:
         logging.info("created Tag successfully for version %d" %(version))
     else:
         logging.error("Please check the version %d" %(version))
	 #print(r.status_code)
     #print(type((r.status_code)))
     return r
 except Exception as e:
	 logging.error('Error Message for MagicDraw is %s' , str(e))
	 sys.exit(1)

#project_id = 'e3ac899c-040c-4267-848a-05a30b10564c'
#project_id = raw_input("Project ID:")
##tag_name = raw_input('Tag Name:')
#tag_description = raw_input('Tag description :')

#################################
# Create Commit Table for choosing Commit Number from Git #
#################################

commits_df = pd.DataFrame(columns = ['repo' , 'commit' , 'date','commitno'])
md_df = pd.DataFrame(columns = ['descriptor','repo','version','commitno'])

##################################
# Creating Release Entry in CMDB #
##################################
logging.info("Running the release script....")

run_command = 'python release-insert.py ' + branch + ' ' + Release_type + ' '
os.system(run_command)

logging.info("finished running release script...")


#################################
# Insert Values into GITHUB API #
#################################
logging.info("Entering into the Main Function")
row = len(data)
data.reset_index(inplace=True,drop=True)
data = data.to_dict(orient = 'index')
print("The number of rows : ")
print(row)
for i in range(0,row):
    discriptor = data[i]['Product_Descriptors']
    repo = data[i]['Product_Descriptor_Level3']
    cmt_no = data[i]['id']
    dfc = data[i]['DEF_Changlist']
    r = dfc.split(";")
    print(repo)
	
    if "MCA Platform SW" in discriptor :
	print("Found Match")
        org = "GET-MCA-PlatformServices"
	logging.info("Verified MCA Platform SW in discriptor")
	for item in r:
     		if any(compiled_reg.search(item) for compiled_reg in git_list):
			version = GetCommit(org,repo,item)
	   		logging.info("Matched git list from the DEF_Changlist")
          	 	#r=CreateBranch(org,repo,branch,version)
           		#CreateTag(org,repo,version,branch,branch)
	   		commits_df.loc[len(commits_df)] = [repo , item , version , cmt_no]
	        elif any(compiled_reg.search(item) for compiled_reg in magicdraw_list):
			logging.info("Matched MD list from the DEF_Changlist")
	                ver = None
	 		try:
				ver = int(re.findall('\d+', item)[0])
			except:
				ver = None
		
        	        md_df.loc[len(md_df)] = [discriptor ,repo , ver , cmt_no]
					
		else:
			logging.error('DEF change List UNKNOWN or null')
			sys.exit(1)
       


	

    elif "MCA System" in discriptor :
	logging.info("Matched MD list from the DEF_Changlist")
        version = None
        try:
		version = int(re.findall('\d+', item)[0])
	except:
		version = None
		md_df.loc[len(md_df)] = [discriptor , repo , version , cmt_no]
        
		

logging.info("Getting Latest Commit No. for Release Branch")
idx = commits_df.groupby(['repo'])['date'].transform(max) == commits_df['date']
print(commits_df[idx])	
latest_df = commits_df[idx].copy()
for i in latest_df.index:
	#logging.info("Creating Release Branch %s" %(repo))
	org = "GET-MCA-PlatformServices"
	repo = latest_df.loc[i,'repo']
	commit_nos = commits_df[commits_df['repo']==repo]['commitno'].unique().tolist()
	description = 'The ClearQuest number(s) : ' + ','.join([str(elem) for elem in commit_nos])
	version = latest_df.loc[i,'commit']
	if repo in repo_dict:
		build = repo_dict[repo]
	else:
		build = checkserviceBuild(org,repo)
		repo_dict[repo] = build
	if (build == 'serviceBuild'):
		r=CreateBranch(org,repo,branch,version)
		CreateTag(org,repo,version,branch,description)
		print(str(r))
		if r.status_code==201:
		     logging.info("created release branch successfully for repo %s" %(repo))
		     logging.info("calling the python script to insert the values into database")
		     run_command = 'python cmdbinsert.py ' + branch + ' ' + version + ' ' + repo + ' ' + "Git" + ' ' + Release_type + ' ' 
		     os.system(run_command)
		elif r.status_code==422:
		     logging.warn("Release branch is already created for repo  %s" %(repo))
		     run_command = 'python cmdbinsert.py ' + branch + ' "' + "Already Created" + '" ' + repo + ' ' + "Git" + ' ' + Release_type + ' '
	             os.system(run_command)
		else:
	  	     logging.error("Please verify the git repo name for repo  %s" %(repo))
		     sys.exit(1)	
        else: 
		CreateTag(org,repo,version,branch,description) 
	        run_command = 'python cmdbinsert.py ' + branch + ' ' + version + ' ' + repo + ' ' + "Other" + ' ' +  Release_type + ' '
                os.system(run_command)

logging.info("Completed getting latest commit number from github")
	
with open('repo_list.pkl', 'wb') as fp:
    pickle.dump(repo_dict, fp)  		
		
		
logging.info("Getting Maximum Version for Magic Draw")
idx2 = md_df.groupby(['repo'])['version'].transform(max) == md_df['version']
print(md_df[idx2])	
latest_df = md_df[idx2].copy()
for i in latest_df.index:
	repo = latest_df.loc[i,'repo']
	ver = latest_df.loc[i,'version']
	descriptor = latest_df.loc[i,'descriptor']
	commit_nos = md_df[md_df['repo']==repo]['commitno'].unique().tolist()
	description = 'The ClearQuest number(s) : ' + ','.join([str(elem) for elem in commit_nos])
	try:
		project_id = projectid_dict[descriptor]
	except:
		print('Null or Not Matching Project Descriptor')
		sys.exit(1)
	ret=MagicDraw(project_id,branch,description,ver)
        if ret.status_code==201:
		logging.info("created Tag successfully for version %d" %(ver))
        	logging.info("calling the python script to insert the values into database")
        	run_command = 'python cmdbinsert.py ' + branch + ' ' + str(ver) + ' "' + str(repo) + '" ' + "MD" + ' ' + Release_type + ' ' 
             	os.system(run_command)

        else:
             	logging.error("Please check the version %d" %(ver))
             	sys.exit(1)


logging.info("Completed getting latest commit number from MagicDraw")
logging.info("All operations completed")   
