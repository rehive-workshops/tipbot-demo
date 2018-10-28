from slackclient import SlackClient
from rehive import Rehive, APIException

import pprint
pp = pprint.PrettyPrinter(indent=4)

SLACK_TOKEN=os.environ.get('SLACK_TOKEN')
REHIVE_TOKEN=os.environ.get('REHIVE_TOKEN')

# instantiate Slack client
slack_client = SlackClient(SLACK_TOKEN)
rehive = Rehive(REHIVE_TOKEN)
# Sends the response back to the channel
users = slack_client.api_call(
    "users.list",
)['members']

users = [user for user in users if not user['deleted'] and not user['is_bot'] and user['name'] != 'slackbot']

for user in users:
	try:
		r = rehive.admin.users.create(
		    id=user['id'],
		    email=user['profile']['email']
		)
	except APIException as e:
		print('Error with ' + user['profile']['email'])
		print(str(e))
