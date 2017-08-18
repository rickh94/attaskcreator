import os
import flask
from flask import g
import re
import json
from flask_slack import Slack
from slackclient import SlackClient
from attaskcreator import atinterface
from attaskcreator import create
from attaskcreator import exceptions

app = flask.Flask(__name__)
app.config.from_object(__name__)

# TODO: These objects need to move
slackin = Slack(app)
mytoken = os.environ['SLACK_VER_TOKEN']
myid = os.environ['TEAM_ID']

slackout = SlackClient(os.environ['SLACK_API_TOKEN'])


# THIS FUNCTION DOESN'T WORK AT ALL. NEED TO IPLEMENT EVERYTHING.
# TODO: figure out how slack reports/handles attachments
@slackin.command('task', token=mytoken, team_id=myid, methods=['POST'])
def task(**kwargs):
    text = kwargs.get('text')
    # returns an array of SlackPerson objects
    people, parse_text = findpeople(text)
    people_rec_ids = []
    all_users = slackout.api_call('users.list')
    for person in people:
        person.get_slack_id(all_users)
        person.get_info(slackout)
        # at some point set g to the database (start using g in config.py)
        person_rec = g.atdb.search_for_email(person.email)
        people_rec_ids.append(person_rec)

    # actual text parsing. Should always return but strip out phrase if needed.
    final_text = parse_message(parse_text)
    # many options here will come from global config.
    try:
        g.atdb.create_task_record(
            g.task_table,
            (g.text_field, final_text),
            (g.person_field, people_rec_ids),
            (g.notes_field, text),
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
    return slackin.response("A record was created and you message was sent.")
