#!/usr/bin/python3
### NX-OS API Explorer
### Nicholas Schmidt
### 04 Jun 2020

# API Processing imports
import requests
import json

# Command line parsing imports
import argparse

# Command line validating imports
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

# Arguments Parsing
parser = argparse.ArgumentParser(description='Fetch all routing tables via NX-API')
parser.add_argument('-v', '--verbosity', action='count', default=0, help='Output Verbosity')
parser.add_argument('-f', help='Select JSON Payload file')
subparsers = parser.add_subparsers(help='Use Basic or CA Authentication')
unpw = subparsers.add_parser('basic', help='Use Basic Authentication')
unpw.add_argument('-u', help='NX-API Username')
unpw.add_argument('-p', help='NX-API Password')
cert = subparsers.add_parser('ca', help='Use Certificate Authentication')
cert.add_argument('--cert', help='NX-API Client Certificate. Required if using CA Authentication')
cert.add_argument('--privkey', help='NX-API Client Certificate Private Key. Required if using CA Authentication')
cert.add_argument('--ca', help='NX-API Client Certificate CA. Optional if using CA Authentication')
parser.add_argument('nxapi_endpoint', help='The NX-API Endpoint to target with this API call')

args = parser.parse_args()

# Ensure that NX-API Endpoint is a valid one
validate = URLValidator()
try:
  validate(args.nxapi_endpoint)
except:
  print('Invalid URL. Please try a valid URL. Example: "http://10.1.1.1/ins"')
  exit()

# Set HTTP Error + Verbosity table. Due to the use of max(min()), verbosity count becomes a numerical range that caps off and prevents array issues
# Credit where due - https://gist.github.com/bl4de/3086cf26081110383631 by bl4de
httperrors = {
  100: ('Continue', 'Request received, please continue'),
  101: ('Switching Protocols',
        'Switching to new protocol; obey Upgrade header'),

  200: ('OK', 'Request fulfilled, document follows'),
  201: ('Created', 'Document created, URL follows'),
  202: ('Accepted',
        'Request accepted, processing continues off-line'),
  203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
  204: ('No Content', 'Request fulfilled, nothing follows'),
  205: ('Reset Content', 'Clear input form for further input.'),
  206: ('Partial Content', 'Partial content follows.'),

  300: ('Multiple Choices',
        'Object has several resources -- see URI list'),
  301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
  302: ('Found', 'Object moved temporarily -- see URI list'),
  303: ('See Other', 'Object moved -- see Method and URL list'),
  304: ('Not Modified',
        'Document has not changed since given time'),
  305: ('Use Proxy',
        'You must use proxy specified in Location to access this '
        'resource.'),
  307: ('Temporary Redirect',
        'Object moved temporarily -- see URI list'),

  400: ('Bad Request',
        'Bad request syntax or unsupported method'),
  401: ('Unauthorized',
        'No permission -- see authorization schemes'),
  402: ('Payment Required',
        'No payment -- see charging schemes'),
  403: ('Forbidden',
        'Request forbidden -- authorization will not help'),
  404: ('Not Found', 'Nothing matches the given URI'),
  405: ('Method Not Allowed',
        'Specified method is invalid for this server.'),
  406: ('Not Acceptable', 'URI not available in preferred format.'),
  407: ('Proxy Authentication Required', 'You must authenticate with '
        'this proxy before proceeding.'),
  408: ('Request Timeout', 'Request timed out; try again later.'),
  409: ('Conflict', 'Request conflict.'),
  410: ('Gone',
        'URI no longer exists and has been permanently removed.'),
  411: ('Length Required', 'Client must specify Content-Length.'),
  412: ('Precondition Failed', 'Precondition in headers is false.'),
  413: ('Request Entity Too Large', 'Entity is too large.'),
  414: ('Request-URI Too Long', 'URI is too long.'),
  415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
  416: ('Requested Range Not Satisfiable',
        'Cannot satisfy request range.'),
  417: ('Expectation Failed',
        'Expect condition could not be satisfied.'),

  500: ('Internal Server Error', 'Server got itself in trouble'),
  501: ('Not Implemented',
        'Server does not support this operation'),
  502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
  503: ('Service Unavailable',
        'The server cannot process the request due to a high load'),
  504: ('Gateway Timeout',
        'The gateway server did not receive a timely response'),
  505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}

# Set NX-API Credential Variables
client_cert_auth=False
switchuser=args.u
switchpassword=args.p
client_cert='PATH_TO_CLIENT_CERT_FILE'
client_private_key='PATH_TO_CLIENT_PRIVATE_KEY_FILE'
ca_cert='PATH_TO_CA_CERT_THAT_SIGNED_NXAPI_SERVER_CERT'

# Set NX-API URL and payload
# Note: default API URI endpoint for NX-OS is /ins

# Attempt to load a json file, and lint it
try:
    with open(args.f) as json_file:
        payload = json.load(json_file)
except ValueError as err:
    print('Python thinks you have a json formatting issue. Please run your payload input through a json linter.')
    print(err)
    exit()
except IOError as err:
    print('A File I/O error has occurred. Please check your file path!')
    print(err)
    exit()
except:
    print('An unexpected error has occurred!')
    exit()

# Set headers and target for immediate processing
url=args.nxapi_endpoint
myheaders={'content-type':'application/json'}

# Create a JSON file if a developer wants to use this from the python code (it's sometimes easier)
#with open('payload_show_ip_route_vrf_all.json', 'w') as outfile:
#    json.dump(payload, outfile)

# Perform NX-API Processing - conditional basic or certificate authentication
try: 
  if client_cert_auth is False:
    response_response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword))
  else:
    response_response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword),cert=(client_cert,client_private_key),verify=ca_cert)
  # We'll be discarding the actual `Response` object after this, but we do want to get HTTP status for erro handling
  response_code = response_response.status_code
  response_response.raise_for_status() #trigger an exception before trying to convert or read data. This should allow us to get good error info
  response_json = response_response.json() #if HTTP status is good, i.e. a 100/200 status code, we're going to convert the response into a json dict
except:
  if httperrors.get(response_code):
    print ('HTTP Status Error ' + str(response_code) + ' ' + httperrors.get(response_code)[max(min(args.verbosity,1),0)])
    exit() #interpet the error, then close out so we don't have to put all the rest of our code in an except statement
  else:
    print ('Unhandled HTTP Error ' + str(response_code) + '!' )
    exit() #interpet the error, then close out so we don't have to put all the rest of our code in an except statement

# Begin Processing API Data
## Debugging shouldn't require code changes, let's use our verbosity switches
if max(min(args.verbosity,1),0) >= 1:
      print (response_json) #print raw json response
