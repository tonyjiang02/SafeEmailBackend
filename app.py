import os

from flask import Flask, request, redirect
import threading
from firebase_admin import credentials, firestore, initialize_app
from flask_cors import CORS

import email_util
import ml_approve

app = Flask(__name__)
cors = CORS(app)

email_util.init()

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
users = db.collection('users')


@app.route('/message_send', methods=('POST',))
def message_send():
    msg = request.form['msg']
    to_id = request.form['to_id']
    from_email = request.form['from_email']

    from_id = user_from_email(from_email)['id']

    def inner():
        user = user_from_id(to_id)

        categories = ['TOXICITY', 'SEVERE_TOXICITY', 'INSULT', 'PROFANITY', 'THREAT', 'SEXUALLY_EXPLICIT']
        # categories = [v for v in categories if user[v.lower()]]
        ml_approved, probabilities = ml_approve.approval_request(msg, categories)

        if ml_approved:
            send(msg, to_id, from_id, from_email)
        else:
            squad_emails = user_from_id(to_id)['friends']
            email_util.send_squad_approval(squad_emails, msg, to_id, from_id, from_email,
                                           zip(categories, probabilities))

    threading.Thread(target=inner, daemon=True).start()

    return {}


@app.route('/approve')
def approve():
    msg = request.args['msg']
    to_id = request.args['to_id']
    from_id = request.args['from_id']
    from_email = request.args['from_email']

    send(msg, to_id, from_id, from_email)

    return redirect('https://squadtalk.tech/sendMessage.html')


def send(msg, to_id, from_id, from_email):
    email = user_from_id(to_id)['email']

    email_util.send_message(msg, to_id, email, from_id, from_email)


@app.route('/reject')
def reject():
    return redirect('https://squadtalk.tech/blockMessage.html')


def user_from_id(id_):
    for u in users.stream():
        d = u.to_dict()
        if d['id'] == id_:
            return d


def user_from_email(email):
    for u in users.stream():
        d = u.to_dict()
        if d['email'] == email:
            return d


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
