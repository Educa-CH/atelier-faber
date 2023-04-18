from flask import Flask, render_template, jsonify, session, request
from configparser import ConfigParser
import requests
import json
import os
import time

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])      
def name():
    create_connection_invitation()

    while check_connection() != 'established':
        time.sleep(2)


    if request.method == 'POST':
        name = request.form['name']
        url = issuer_url + '/issue/process'
        data = {
            "connectionId": session['connection'],
            "credentialDefinitionId": cred_def,
            "attributes": {
                attr1: name,
                attr2: value2,
                attr3: value3
            },
            "userId": "Anonymous"
        }
        print(data)

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            url,
            json=data,
            headers=headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            session['processId'] = data['processId']

            return render_template('loading.html')

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

    if os.path.getsize(file_name) == 0 and response.status_code == 200:
        with open(file_name, 'w') as file:
            file.write(response.text)
        return 'Message written to file.'
    else:
        return 'File already has content. Nothing was written.'

    return "done"

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

    if state == 'active':
        return 'established'
    else:
        return 'waiting'


if __name__ == "__main__":
    app.run(port=5001)
    app.run(debug=False)  