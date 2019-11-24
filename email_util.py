import smtplib
from urllib.parse import urlencode

from mako.template import Template
from sendgrid import SendGridAPIClient, Mail

smtp_server = 'smtp.semdgrid.net'

server: smtplib.SMTP_SSL

sender: str

backend_ip = '192.168.137.28:8080'

sg = SendGridAPIClient('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')


def read(file):
    with open(file) as f:
        return f.read()


formats = {'squad': {'txt': Template(filename='email_formats/squad_approval/body.txt', input_encoding='utf-8'),
                     'html': Template(filename='email_formats/squad_approval/body.html', input_encoding='utf-8')},
           'message': {'txt': Template(filename='email_formats/message/body.txt', input_encoding='utf-8'),
                       'html': Template(filename='email_formats/message/body.html', input_encoding='utf-8')}
           }


def send_email(to, subject, txt, html=''):
    message = Mail(
        from_email='approval@squadtalk.tech',
        to_emails=to,
        subject=subject,
        html_content=html,
        plain_text_content=txt)
    sg.send(message)


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
    send_email('squaddtalk@gmail.com', 'test', 'test', '<h1>test</h1>')
