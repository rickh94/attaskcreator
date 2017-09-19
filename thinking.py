import os
import flask
import re
import json
import slackmentions
from flask import g
from flask_slack import Slack
from attaskcreator import config
from attaskcreator import exceptions
from slackclient import SlackClient
from slackperson import SlackPerson


app = flask.Flask(__name__)
app.config.from_object(__name__)

slackin = Slack(app)
app.config['SLACK_VER_TOKEN'] = os.environ['SLACK_VER_TOKEN']
app.config['TEAM_ID'] = os.environ['TEAM_ID']
slackout = SlackClient(os.environ['SLACK_API_TOKEN'])
app.config['CONFIG_PATH'] = os.environ['ATTASK_CONFIG_PATH']


def setup():
    settings = config.Settings(path_prefix=app.config['CONFIG_PATH'])
    settings.setup_log()
    settings.setup_db()
    settings.setup_phrases()
    settings.setup_aws()
    settings.setup_tables()
    return settings


@slackin.command('echo', token=app.config['SLACK_VER_TOKEN'],
                 team_id=app.config['TEAM_ID'], methods=['POST'])
def echo_back(**kwargs):
    print(kwargs)
    settings = setup()
    text = kwargs.get('text')
    # returns an array of SlackPerson objects
    all_users = slackout.api_call('users.list')
    people = slackmentions.findpeople(text, all_users)
    if people == []:
        raise exceptions.NoMentionsError(
            "No one was mentioned in the message")

    # algorithm for replacing plain text @mentions with real ones
    # print(people)
    people_ids = []
    for person in people:
        # clean up the text
        echo_text = slackmentions.mention_text(text, people=people)
        clean_text = slackmentions.clean_text(text, people=people)
        person_id = settings.database.search_for_email(
            settings.at_people_table,
            (settings.people_table_key, person.email),
            ("First Name", person.fname),
            ("Last Name", person.lname)
        )
        people_ids.append(person_id)

    # print(people_ids)
    notes_info = ()
    if settings.tasks_table_notes is not None:
        notes_info = (settings.tasks_table_notes, text)

    # implement this at some point
    file_info = ()
    settings.database.create_task_record(
        settings.at_tasks_table,
        (settings.tasks_table_text, clean_text),
        (settings.tasks_table_person, people_ids),
        notes_info,
        file_info,
    )

    print(slackout.api_call("chat.postMessage",
                            text=' '.join((echo_text, 'CLEANED:', clean_text)),
                            channel=kwargs.get('channel_id'),
                            reply_broadcast=True,
                            as_user=True,
                            ))
    return slackin.response('Your message was sent', response_type='ephemeral')


app.add_url_rule('/', view_func=slackin.dispatch)
# if __name__ == '__main__':
#     app.run()
