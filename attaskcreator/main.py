import os
import flask
import re
import json
from flask_slack import Slack
from slackclient import SlackClient

app = flask.Flask(__name__)
app.config.from_object(__name__)

slackin = Slack(app)
mytoken = os.environ['SLACK_VER_TOKEN']
myid = os.environ['TEAM_ID']

slackout = SlackClient(os.environ['SLACK_API_TOKEN'])


# THIS FUNCTION DOESN'T WORK AT ALL. NEED TO IPLEMENT EVERYTHING.
@slackin.command('task', token=mytoken, team_id=myid, methods=['POST'])
def task(**kwargs):
    text = kwargs.get('text')
    # returns an array of SlackPerson objects
    people, new_text = findpeople(text)
