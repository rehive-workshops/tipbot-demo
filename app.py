import os
import time
import re
from slackclient import SlackClient
from rehive import Rehive

from decimal import Decimal

from logging import getLogger
logger = getLogger()

SLACK_TOKEN=os.environ.get('SLACK_TOKEN')
REHIVE_TOKEN=os.environ.get('REHIVE_TOKEN')

rehive = Rehive(REHIVE_TOKEN)
# instantiate Slack client
slack_client = SlackClient(SLACK_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def to_cents(amount: Decimal, divisibility: int) -> int:
    return int(amount * Decimal('10')**divisibility)


def from_cents(amount: int, divisibility: int) -> Decimal:
    return Decimal(amount) / Decimal('10')**divisibility


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"], event["user"]
            if event["channel"].startswith('D'):
                return event["text"], event["channel"], event["user"]
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    print(message_text)
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    elif command.startswith('balance'):
        try:
            r = rehive.admin.accounts.get(filters={"user":user, "primary": True})
            reference = r[0]['reference']
            r = rehive.admin.accounts.obj(reference).currencies.get(filters={"active": True})
            divisibility = r[0]['currency']['divisibility']
            currency = r[0]['currency']['code']
            balance = from_cents(r[0]['balance'], divisibility)

            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text="Let me check..."
            )
            response = "Your balance is {} {}".format(str(balance), currency)
        except Exception as e:
            logger.exception(e)
            response = "Oops something went wrong, I wasn't able to look up you balance"

    elif command.startswith('give') or command.startswith('send') or command.startswith('tip'):
        try:
            match = re.search('<@(|[WU].+?)>\s*([0-9]{1,9}(?:\.[0-9]{0,16})?)\s*(xlm|XLM)', command)
            recipient = match.group(1)
            amount = match.group(2)
            currency = match.group(3)
        except Exception as e:
            response = "I don't understand you, please rephrase."
            logger.exception(e)

        try:
            r = rehive.admin.accounts.get(filters={"user":user, "primary": True})
            reference = r[0]['reference']
            r = rehive.admin.accounts.obj(reference).currencies.get(filters={currency: currency})
            divisibility = r[0]['currency']['divisibility']

            amount_cents = to_cents(Decimal(str(amount)), divisibility)

            rehive.admin.transactions.create_transfer(
                user=user,
                amount=amount_cents,
                currency=currency.upper(),
                recipient=recipient
            )

            response = "Ok, I've gone ahead and sent {} {} to <@{}>.".format(amount, currency, user)

        except Exception as e:
            logger.exception(e)
            response = "Oops something went wrong, I wasn't able to execute the transaction."


    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, user = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")