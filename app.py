from flask import Flask, render_template, jsonify, session, request, url_for
import qrcode
import requests
import json


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
        #issue the credential
        pass
    else:
        #just show the page
        return render_template('name.html')

    

  

if __name__ == "__main__":
    app.run(debug=True)    