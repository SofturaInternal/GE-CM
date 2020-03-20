import requests
def checkserviceBuild():
	url = 'https://github.build.ge.com/raw/GET-MCA-PlatformServices/gets-config/master/Jenkinsfile'
	headers = {'Authorization': 'token 6df8e6858e395acff14f29cbecf976e3eeec2650', 'content-type': 'application/json'}
	response = requests.get(url,headers=headers)
	if response.status_code==200:
	   print("Got the latest commit number from the develop branch for ")
	else:
	   print("Something is wrong with the repo name, verify it")

	print("Reading the contents of jenkins")
	jenkinsfile_text = response.text

	if "serviceBuild" in jenkinsfile_text:
		return 'servicebuild'
	elif "cotsBuild" in jenkinsfile_text:
		return 'cotsBuild'
	elif "libraryBuild" in jenkinsfile_text:
		return 'libraryBuild'
	else:
		return 'Unknown'

ret = checkserviceBuild()
print ret
