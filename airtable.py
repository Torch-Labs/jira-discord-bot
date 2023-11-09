import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

app_id = "appwSSjovGODhjRBP"
table_id = "tblwq7fJoxj59YrAD"

token = os.getenv("airtable_token")
if not token:
    token = ""


def get_record(email):
    url = f"https://api.airtable.com/v0/{app_id}/{table_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(url, headers=headers)
    data = json.loads(r.text)
    if r.status_code != 200:
        return (False)
    for record in data['records']:
        if "Email" in record['fields']:
            print(record)
            if record['fields']['Email'] == email:
                record_url = f"https://airtable.com/{app_id}/{table_id}/{record['id']}"
                firbase_id = None
                if "Firebase UID" in record['fields']:
                    firbase_id = record['fields']['Firebase UID']
                return (record_url, firbase_id)
    return ("invalid email")
