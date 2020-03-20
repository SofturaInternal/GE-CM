import pickle



with open('repo_list.pkl','rb') as f:
	repo_dict = pickle.load(f)

print(repo_dict)
