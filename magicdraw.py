import requests
import json
import urllib3
from requests.auth import HTTPBasicAuth



 
######################
#Connect to MagicDraw
######################

def MagicDraw(project_id,tag_name,tag_description,version):
  url = 'https://3.125.182.25:8111/osmc/resources/'+project_id+'/tags'
  payload = {
    "@type": ["ldp:DirectContainer", "kerml:Tag"],
    "dcterms:title": tag_name,
    "dcterms:description": tag_description,
    "commitID": version,
    "@context": "http://3.125.182.25:8111/osmc/schemas/tag"
  }
  headers = {'accept':'application/ld+json', 'content-type': 'application/ld+json'}
  r = requests.post(url, data=json.dumps(payload), headers=headers,auth=HTTPBasicAuth('mgurumurthy','Letmein!234'),verify=False)
  #print(r.status_code)
  #print(type((r.status_code)))
  return r

###############################
#Insert the values of MagicDraw
###############################

project_id = raw_input("Project ID:")
tag_name = raw_input('Tag Name:')
tag_description = raw_input('Tag description :')
version = raw_input('Enter the Version Number:')
version = int(float(version))
r=MagicDraw(project_id,tag_name,tag_description,version)

if r.status_code==201:
  print("created Tag successfully for version %d" %(version))
elif r.status_code==404:
  print("Please check the version %d" %(version))
else:
  print("Failed to create the tag")
exit(1)

'''
if '201' in rc:
  print("created Tag successfully for version %s" %(version))
 elif '422' in rc:
  print("Branch already exists for version %s" %(version))
 else:
  print("Failed to create branch for version %s" %(version))
exit(1)
'''
