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
