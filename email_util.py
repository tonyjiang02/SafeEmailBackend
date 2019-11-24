import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode
from mako.template import Template

smtp_server = 'smtp.gmail.com'

server: smtplib.SMTP_SSL

sender: str

backend_ip = '192.168.137.28:8080'


def read(file):
    with open(file) as f:
        return f.read()


formats = {'squad': {'txt': Template(filename='email_formats/squad_approval/body.txt', input_encoding='utf-8'),
                     'html': Template(filename='email_formats/squad_approval/body.html', input_encoding='utf-8')},
           'message': {'txt': Template(filename='email_formats/message/body.txt', input_encoding='utf-8'),
                       'html': Template(filename='email_formats/message/body.html', input_encoding='utf-8')}
           }


def init():
    with open('gmail_auth') as f:
        global sender
        sender = f.readline()
        password = f.readline()

    global server
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_server, 465, context=context)
    server.login(sender, password)


def send_email(to, subject, txt, html=''):
    msg = EmailMessage()
    msg.set_content(txt)
    if html:
        msg.add_alternative(html, subtype='html')

    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = sender

    server.sendmail(sender, [to], msg.as_string())


categories_trans = {'TOXICITY': 'Toxic',
                    'SEVERE_TOXICITY': 'Very Toxic',
                    'INSULT': 'Insult',
                    'PROFANITY': 'Profanity',
                    'THREAT': 'Threat',
                    'SEXUALLY_EXPLICIT': 'Inappropriate'}


def send_squad_approval(squad_emails, msg, to_id, from_id, from_email, probabilities):
    payload = {'msg': msg, 'to_id': to_id, 'from_id': from_id, 'from_email': from_email}
    approve_url = f'http://{backend_ip}/approve?{urlencode(payload)}'
    reject_url = f'http://{backend_ip}/reject'

    probabilities = {categories_trans[k]: int(v * 100) for k, v in probabilities}
    format_map = {'msg': msg, 'approve_url': approve_url, 'from_id': from_id, 'to_id': to_id,
                  'reject_url': reject_url, 'probabilities': probabilities}
    txt = formats['squad']['txt'].render(**format_map)
    html = formats['squad']['html'].render(**format_map)

    for a in squad_emails:
        send_email(a, f'Approval for Message from {from_id} to {to_id}', txt, html)


def send_message(msg, to_id, to_email, from_id, from_email):
    format_map = {'msg': msg, 'from_id': from_id, 'to_id': to_id, 'from_email': from_email}
    txt = formats['message']['txt'].render(**format_map)
    html = formats['message']['html'].render(**format_map)

    send_email(to_email, f'Message from {from_id}', txt, html)


def close():
    server.close()


if __name__ == '__main__':
    # testing
    init()
    send_email('squaddtalk@gmail.com', 'test', 'test', '<h1>test</h1>')
