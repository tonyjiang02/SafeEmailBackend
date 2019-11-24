import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode

smtp_server = 'smtp.gmail.com'

server: smtplib.SMTP_SSL

sender: str


def read(file):
    with open(file) as f:
        return f.read()


formats = {'squad': {'txt': read('email_formats/squad_approval/body.txt'),
                     'html': read('email_formats/squad_approval/body.html')},
           'message': {'txt': read('email_formats/message/body.txt'),
                       'html': read('email_formats/message/body.html')}
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


def send_squad_approval(squad_emails, msg, to_name, from_name, to_id, from_id, from_email):
    payload = {'msg': msg, 'to_id': to_id, 'from_id': from_id, 'from_email': from_email}
    approve_url = f'http://localhost:5000/approve?{urlencode(payload)}'
    reject_url = 'http://localhost:5000/reject'

    format_map = {'msg': msg, 'approve_url': approve_url, 'from_name': from_name, 'to_name': to_name,
                  'reject_url': reject_url}
    txt = formats['squad']['txt'].format_map(format_map)
    html = formats['squad']['html'].format_map(format_map)

    for a in squad_emails:
        send_email(a, f'Approval for Message from {from_name} to {to_name}', txt, html)


def send_message(msg, to_name, to_email, from_name, from_email):
    format_map = {'msg': msg, 'from_name': from_name, 'to_name': to_name, 'from_email': from_email}
    txt = formats['message']['txt'].format_map(format_map)
    html = formats['message']['html'].format_map(format_map)

    send_email(to_email, f'Message from {from_name}', txt, html)


def close():
    server.close()


if __name__ == '__main__':
    # testing
    init()
    send_email('squaddtalk@gmail.com', 'test', 'test', '<h1>test</h1>')
