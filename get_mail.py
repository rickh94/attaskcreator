import smtplib, time, imaplib, email
import configparser
import html2text

# class EmailINeed():
    # def __init__(headers, content):

def get_login():
    config = configparser.ConfigParser()
    config.read("./login.conf")

    return (
            config['login']['user'],
            config['login']['password'],
            config['server']['imap_url'],
            int(config['server']['port'])
            )

FROM_EMAIL, FROM_PWD, SMTP_SERVER, SMTP_PORT = get_login()

def get_text(mess):
    if mess.is_multipart():
        return get_text(mess.get_payload(0))
    else:
        return mess.get_payload(None, True)

def readmail():
    # try:
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(FROM_EMAIL, FROM_PWD)
    mail.select('Inbox')

    typ, data = mail.search(None, 'UnSeen')

    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                email_from = msg['from']
                print('From: ' + email_from)
                print('Subject: ' + email_subject)
                print('To: ' + msg['to'])
                print(html2text.html2text(str(get_text(msg))))
                print('')

        mail.store(num, '+FLAGS', '\Seen')

    # except Exception as e:
    #     print(str(e))
    mail.close()

readmail()
