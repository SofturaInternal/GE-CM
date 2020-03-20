import jenkinsapi
import requests
from jenkinsapi.jenkins import Jenkins

jenkins_url = 'http://bng1getransci.jfwtc.ge.com:9080/MCAPh2/'
server = Jenkins(jenkins_url, username = '503135589', password = 'g26Jan@1993m')   # your github credentials.

job_instance = server.get_job('GET-MCA-PlatformServices/gets-filetransferservice/IVV-PLT-2019.36')
running = job_instance.is_queued_or_running()
if not running:
    latestBuild = job_instance.get_last_build()
    latestBuildStatus = latestBuild.get_status()
    #print latestBuild.get_status()
    print(latestBuildStatus)
    print(latestBuild)
