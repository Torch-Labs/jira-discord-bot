import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
import os

load_dotenv()
jira_token = os.getenv("jira_token")
email = os.getenv("email")

if not jira_token:
    jira_token = ""
if not email:
    email = ""

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def create_ticket(name, description):
    data = {
        "fields": {
            "project": {
                "key": "ESR"
            },
            "summary": name,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": description,
                                "type": "text"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Bug"
            }
        }
    }
    url = "https://torchlabsxyz.atlassian.net/rest/api/3/issue/"
    auth = HTTPBasicAuth(email, jira_token)
    response = requests.post(url, json=data, headers=headers, auth=auth)

    if response.status_code == 201:
        new_issue = response.json()
        print(new_issue)
        pull_issue(new_issue['key'])
        return (True)
    else:
        return (False)


def pull_issue(issue):
    url = "https://torchlabsxyz.atlassian.net/rest/agile/1.0/board/2/issue"
    auth = HTTPBasicAuth(email, jira_token)

    payload = json.dumps({
        "issues": [
            issue
        ]
    })

    response = requests.request(
        "POST",
        url,
        headers=headers,
        data=payload,
        auth=auth
    )
    if response.status_code == 201:
        return (True)
    else:
        return (False)
