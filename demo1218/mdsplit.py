dfc = "MD810;a8999999999999999"
ret = dfc.split(";")
print ret[0]
if "MD" in ret[0]:
    print "Found!"
    #CreateTag(org,repo,version,branch,branch)
else:
    print "Repo type"

