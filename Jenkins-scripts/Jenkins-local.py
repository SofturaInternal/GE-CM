import jenkinsapi
import requests
from jenkinsapi.jenkins import Jenkins

jenkins_url = 'http://3.125.182.23:8080/'
server = Jenkins(jenkins_url, username = 'admin', password = 'admin')   # your github credentials.

job_instance = server.get_job('Maven_project')
running = job_instance.is_queued_or_running()
if not running:
    latestBuild = job_instance.get_last_build()
    latestBuildStatus = latestBuild.get_status()
    #print latestBuild.get_status()
    print(latestBuildStatus)
    print(latestBuild)
