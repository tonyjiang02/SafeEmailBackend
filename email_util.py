import smtplib
import ssl
from email.message import EmailMessage

smtp_server = 'smtp.gmail.com'

server: smtplib.SMTP_SSL

sender: str


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


def close():
    server.close()


if __name__ == '__main__':
    # testing
    init()
    send_email('squaddtalk@gmail.com', 'test', 'test', '<h1>test</h1>')

