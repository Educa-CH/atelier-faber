from flask import Flask, render_template, jsonify, session, request
from configparser import ConfigParser
import requests
import json
import os
import time

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])      
def name():
    while create_connection_invitation() == 'not available':
        time.sleep(2)

    while check_connection() == 'waiting':
        time.sleep(2)

    connection_id = check_connection()

    if request.method == 'POST':

        creddef_id = get_credential_definition()

        name = request.form['name']
        score = request.form["score"]
        url = 'https://faber-api.educa.ch/issue-credential-2.0/send-offer'

        data = {   
            "connection_id": connection_id, 
            "comment": "Credential offer", 
            "auto_remove": "false", 
            "credential_preview": {
                "@type": "https://didcomm.org/issue-credential/2.0/credential-preview", 
                "attributes": [
                    {
                        "name": "name",
                        "value": name
                    },
                    {
                        "name" : "score",
                        "value": score
                    }
                ]
            },
            "filter": {
                "indy": {
                    "cred_def_id": creddef_id
                }
            },
            "trace": "true"
        }
        headers = {"Content-Type": "application/json"}


        response = requests.post(
            url,
            json=data,
            headers=headers)

        print(data)
        
        if response.status_code == 200:
            return render_template('success.html')

        else:
            return render_template('failure.html')    
    else:
        #just show the page
        return render_template('index.html')       

def create_connection_invitation():
    url = 'https://faber-api.educa.ch/out-of-band/create-invitation'
    data =  {
          "accept": [
               "didcomm/aip1",
                "didcomm/aip2;env=rfc19"
               ],
           "alias": "",
          "handshake_protocols": [
                "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0"
               ],
           "metadata": {},
          "my_label": "Invitation to Alice",
            "protocol_version": "1.1",
            "use_public_did": "false"
          }
    
    print(data)

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        url,
        json=data,
        headers=headers)
    
    file_name = 'connection'

    if response.status_code == 200:
        with open(file_name, 'w') as file:
            file.write(response.text)
        return 'Message written to file.'
    else:
        return 'not available'

def check_connection():
    with open('connection', 'r') as f:
        data = json.load(f)

    # Extract the value of 'connection_id'
    invitation_msg_id = data['invi_msg_id']

    url =  'https://faber-api.educa.ch/connections?invitation_msg_id=' + invitation_msg_id
    
    response = requests.get(url)

    data = json.loads(response.content)

    print(data)

    # Extract the value of 'state'
    state = data['results'][0]['state']
    connection_id = data['results'][0]['connection_id']

    if state == 'active':
        return connection_id
    else:
        return 'waiting'

def get_credential_definition():
    url =  'https://faber-api.educa.ch/credential-definitions/created'
    
    response = requests.get(url)

    data = json.loads(response.content)

    credential_definition_id = data['credential_definition_ids'][0]

    return credential_definition_id
        


if __name__ == "__main__":
    app.run(port=5001, debug=False)