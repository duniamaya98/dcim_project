import requests

NETBOX_URL = "http://10.70.0.20:9008/api/dcim/devices/"
TOKEN = "386ee1eca3f6666c5927b304e7baa12bc27bc259"

headers = {"Authorization": f"Token {TOKEN}"}
res = requests.get(NETBOX_URL, headers=headers).json()

docs = []
for d in res["results"]:
    text = f"""
    Device Name: {d['name']}
    Role: {d['device_role']['name']}
    Site: {d['site']['name']}
    Status: {d['status']['label']}
    """
    docs.append(text)
