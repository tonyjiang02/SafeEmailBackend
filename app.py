import os

from flask import Flask, request, redirect
import threading
from firebase_admin import credentials, firestore, initialize_app
import email_util
import ml_approve

app = Flask(__name__)

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
    from_id = request.form['from_id']
    from_email = request.form['from_email']

    def inner():
        ml_approved = ml_approve.approval_request(msg)

        if ml_approved:
            send(msg, to_id, from_id, from_email)
        else:
            squad_emails = user_from_id(to_id)['friends']
            email_util.send_squad_approval(squad_emails, msg, to_id, from_id, from_email)

    threading.Thread(target=inner, daemon=True).start()

    return {}


@app.route('/approve')
def approve():
    msg = request.args['msg']
    to_id = request.args['to_id']
    from_id = request.args['from_id']
    from_email = request.args['from_email']

    send(msg, to_id, from_id, from_email)

    # TODO: redirect to page on frontend
    return redirect('https://google.com')


def send(msg, to_id, from_id, from_email):
    email = user_from_id(to_id)['email']

    email_util.send_message(msg, to_id, email, from_id, from_email)


@app.route('/reject')
def reject():
    # TODO: redirect to page on frontend
    return redirect('https://google.com')


def user_from_id(id_):
    for u in users.stream():
        d = u.to_dict()
        if d['id'] == id_:
            return d


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
