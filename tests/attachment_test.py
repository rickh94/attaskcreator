import importlib.util
spec = importlib.util.spec_from_file_location("retrieve_mail",
        "../attaskcreator/retrieve_mail.py")
retrieve_mail = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retrieve_mail)
from subprocess import run

user = input("enter username")
password = input("enter password")
mail = retrieve_mail.FetchMail('imap.gmail.com', user, password)

messages = mail.fetch_unread_messages()

for message in messages:
    path = mail.save_attachment(message, "/tmp/downloads/")

    if path is not None:
        run(['nautilus', path])
    else:
        print("no attachment for {}.".format(message))

