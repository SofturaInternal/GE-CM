import pickle


projectid_dict = {}

projectid_dict['MCA Platform SW'] = 'a9f1641e-5994-4065-ac83-5b65dad2e163'
projectid_dict['MCA Application Layer Prod'] = 'e3ac899c-040c-4267-848a-05a30b10564c'
projectid_dict['MCA System'] = 'd215df3d-f670-49dd-9931-f1875c245ce9'
projectid_dict['MCA IVV'] = '66e55a0c-6883-4a79-a16a-c51760aaf9ec'


with open('projectid.pkl' , 'wb') as fp:
	pickle.dump(projectid_dict , fp)