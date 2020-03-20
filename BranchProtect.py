import sys
import requests 

#repo = 'MCA-ConfigurationManagement/CM_Scripts'
#repo = sys.argv[1]
#branch = 'master'
#branch = sys.argv[2]
repo = raw_input('Enter Repo Name:')
branch = raw_input ("Enter Branch Name: ")
access_token = '6df8e6858e395acff14f29cbecf976e3eeec2650'

r = requests.put(
    'https://github.build.ge.com/api/v3/repos/{0}/branches/{1}/protection'.format(repo, branch),
    headers = {
        'Accept': 'application/vnd.github.luke-cage-preview+json',
        'Authorization': 'Token {0}'.format(access_token)
    },
    json = {
        "restrictions": {
            "users": [
              "503135589"
            ],
            "teams": [
              "CM_team"
            ]
        },
        "required_status_checks": None,
        "enforce_admins": True,
"required_pull_request_reviews": {
    "dismissal_restrictions": {
      "users": [
        "503135589"
      ],
      "teams": [
        "CM_team"
      ]
    },
    "dismiss_stale_reviews": True,
    "require_code_owner_reviews": True,
    "required_approving_review_count": 2
  }
    }
)
print(r.status_code)
print(r.json())
