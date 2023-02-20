from flask import Flask, render_template, jsonify, session, request, redirect
import qrcode
import requests
import json
import time


app = Flask(__name__)
app.secret_key = 'thisisthesecretestsecretanybodyhaseversecreted'

@app.route('/')
def index():
    url = 'http://localhost:8080/connection/invitation'
    response = requests.post(url)
    print(response.text)
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
    url = 'http://localhost:8080/connection/' + session.get('connection', None) 
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
        url = 'http://localhost:8100/issue/process'
        data = {
            "connectionId": session['connection'],
            "credentialDefinitionId": "E8sTdcBe7fue6eFaAi231P:3:CL:128085:1.0",
            "attributes": {
                "score": "99"
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
    url = 'http://localhost:8100/issue/process/' + session['processId'] + '/state'
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
    app.run(debug=True)    