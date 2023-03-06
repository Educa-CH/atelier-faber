from flask import Flask, render_template, jsonify, session, request
from configparser import ConfigParser
import qrcode
import requests
import json


app = Flask(__name__)

config = ConfigParser()
config.read('config.ini')
app.secret_key = config.get('DEFAULT', 'SECRET_KEY', )
connection_url = config.get('ENDPOINTS', 'CONNECTION_URL').strip("'")
issuer_url = config.get('ENDPOINTS', 'ISSUER_URL').strip("'")
cred_def = config.get('CREDENTIAL_DEFINITION', 'CREDENTIAL_DEFINITION').strip("'")
attr1 = config.get('ATTRIBUTES', 'ATTR1').strip("'")
attr2 = config.get('ATTRIBUTES', 'ATTR2').strip("'")
attr3 = config.get('ATTRIBUTES', 'ATTR3').strip("'")
value2 = config.get('VALUES', 'VALUE2').strip("'")
value3 = config.get('VALUES', 'VALUE3').strip("'")

# allow site to be embedded in educa.ch 
# potentially used to emebed as iFrame
    #@app.after_request
    #def add_header(response):
    #    response.headers['X-Frame-Options'] = 'ALLOW-FROM https://educa.ch'
    #    return response

@app.route('/')
def index():
    url = connection_url+ '/connection/invitation'
    response = requests.post(url)
    data = json.loads(response.text)
    dynamic_url = data['invitationUrl']
    session['connection'] = data['connectionId']
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=4)
    qr.add_data(dynamic_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("static/images/dynamic_url_qr.png")  # Save the QR code image to a file

    return render_template('index.html', qr_image='static/images/dynamic_url_qr.png')

@app.route('/check_connection/')
def check_connection():
    # Check the connection status by making a GET request to the API endpoint
    url = connection_url+  '/connection/' + session['connection'] 
    response = requests.get(url)
    if response.text == '"established"':
        # Connection has been established
        return jsonify({'status': 'connected'})
    else:
        # Connection has not been established
        return jsonify({'status': 'not connected'})

@app.route('/name', methods=['POST', 'GET'])      
def name():
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
        return render_template('name.html')


@app.route('/loading/')
def loading():
    # Check the Acception status by making a GET request to the API endpoint
    url = issuer_url+ '/issue/process/' + session['processId'] + '/state'
    response = requests.get(url)
    if response.text != '"IN_PROGRESS"':
        # Credential has been accepted
        return jsonify({'status': 'accepted'})
    else:
        # Credential has not been accepted
        return jsonify({'status': 'not accepted'})

@app.route('/success')
def success():
    return render_template('success.html')        
  

if __name__ == "__main__":
    app.run(debug=False)    