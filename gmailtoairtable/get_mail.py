import smtplib, time, imaplib, email
import configparser
from html2text import html2text

# class EmailINeed():
    # def __init__(headers, content):

def get_login():
    config = configparser.ConfigParser()
    config.read("./login.conf")
    # config.read("/etc/gmailtoairtable/login.conf")

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
        return mess.get_payload(None, True).decode('utf-8')

def readmail():
    mail_info = []
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(FROM_EMAIL, FROM_PWD)
    mail.select('Inbox')

    typ, data = mail.search(None, 'UnSeen')

    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)')

        for response_part in data:
            dict_of_data = {}
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                # for k, v in msg.items():
                #     print(k, ':', v)
                dict_of_data['from'] = msg['from']
                dict_of_data['to'] = msg['to']
                dict_of_data['subject'] = msg['subject']
                dict_of_data['date'] = msg['date']
                dict_of_data['body'] = html2text(get_text(msg))
                mail_info.append(dict_of_data)

        mail.store(num, '+FLAGS', '\Seen')

    mail.close()
    return mail_info

def main():
    some_email = readmail()
    # debugging code
    # for mess in some_email:
    #     for k, v in mess.items():
    #         print(k, ':', v)

if __name__ == "__main__":
    main()
