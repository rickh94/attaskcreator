import os
import flask
from flask import g
import re
import json
from flask_slack import Slack
from slackclient import SlackClient
from slackperson import SlackPerson
from attaskcreator import atinterface
from attaskcreator import create
from attaskcreator import exceptions
from attaskcreator import config


app = flask.Flask(__name__)
app.config.from_object(__name__)

# TODO: These objects need to move
slackin = Slack(app)


def setup():
    app.config['vertoken'] = os.environ['SLACK_VER_TOKEN']
    app.config['teamid'] = os.environ['TEAM_ID']
    slackout = SlackClient(os.environ['SLACK_API_TOKEN'])
    # TODO: download and pass stuff first
    # Admittedly, this is a bit of a hack.
    g.settings = config.Settings()
    g.settings.setup_log()
    g.settings.setup_aws()
    g.settings.setup_db()
    g.settings.setup_phrases()
    g.settings.setup_tables()


# THIS FUNCTION DOESN'T WORK AT ALL. NEED TO IPLEMENT EVERYTHING.
# TODO: figure out how slack reports/handles attachments
@slackin.command('task', token=app.config['vertoken'],
                 team_id=app.config['teamid'], methods=['POST'])
def task(**kwargs):
    text = kwargs.get('text')
    # returns an array of SlackPerson objects
    all_users = slackout.api_call('users.list')
    people = findpeople(text, all_users)
    if people == []:
        raise exceptions.NoMentionsError("No one was mentioned in the message")
    for person in people:
        # at some point set g to the database (start using g in config.py)
        person_rec = g.settings.atdb.search_for_email(person.email)
        people_rec_ids.append(person_rec)

    # actual text parsing. Should always return but strip out phrase if needed.
    final_text = parse_message(parse_text)
    # many options here will come from global config.
    try:
        g.settings.atdb.create_task_record(
            g.settings.task_table,
            (g.settings.text_field, final_text),
            (g.settings.person_field, people_rec_ids),
            (g.settings.notes_field, text),
        )
    except exceptions.FailedToCreateError:
        # TODO: add button for 'try again' or 'send message anyway'
        return slackin.response("Your message failed to create a record for "
                                "some reason.")

    # this posts the message to wherever the command was called from
    # (hopefully).
    slackout.api_call("chat.postMessage",
                      text=echo_text,
                      channel=kwargs.get('channel_id'),
                      reply_broadcast=True,
                      as_user=True,
                      )
    return slackin.response("A record was created and your message was sent.")


def findpeople(text, userlist):
    """Return SlackPerson objects for everyone found.

    Arguments:
    text: text to find @ mentions in.
    userlist: output of slack api users.list

    Returns: List of SlackPerson objects or empty list.
    """
    usernames = re.findall('@([a-zA-Z0-9-._]*)', text)
    person_list = [SlackPerson(user, userlist) for user in usernames]
    newtext = text
    for person in person_list:
        newtext = newtext.replace('@' + person.username,
                                  '<@{}>'.format(person.userid))
    return person_list

if __name__ == '__main__':
    setup()
