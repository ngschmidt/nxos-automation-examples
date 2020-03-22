import requests

url = 'http://10.7.28.99/restconf/data/Cisco-NX-OS-device:System/'

payload = """"""

headers = { 
   'Content-Type': 'application/yang.data+json',
   'Accept': 'application/yang.data+json',
   'Cache-Control': 'no-cache'
}

response = requests.request('POST', url, data=payload, headers=headers, auth=(USERID, PASSWORD))

print(response.text) 

print(response.headers['Status'])