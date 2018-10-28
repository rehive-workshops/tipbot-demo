import os
import time
import re
from rehive import Rehive
import pprint
pp = pprint.PrettyPrinter(indent=4)

# Create a company on dashboard.rehive.com
# ADD BCH as acurrency
# Create an account configuration

REHIVE_TOKEN=os.environ.get('REHIVE_TOKEN')

API_KEY=REHIVE_TOKEN
rehive = Rehive(API_KEY)


# Creating users:
#response = rehive.user.emails.get()

# response = rehive.admin.users.create(
#     id="U1QCNFM60",
#     email='michail@rehive.com'
# )
# pp.pprint(response)


# Deposit:
# response = rehive.admin.transactions.create_credit(
#     user="@michail",
#     amount=1000,
#     currency="BCH",
#     status="Complete"
# ) # 1000 satoshis
# pp.pprint(response)

#Specific user's account
# response = rehive.admin.accounts.get(filters={"user":"U1QCNFM60", "primary": True})
# pp.pprint(response)

# reference = response[0]['reference']
# response = rehive.admin.accounts.obj(reference).currencies.get(filters={"active": True})

# balance = response[0]['balance']
# pp.pprint(response)
# print("Balance: " + str(balance))

# Create a second user:
# response = rehive.admin.users.create(
#     username="@bob",
# )	
# pp.pprint(response)

# Send tip from @michail to @bob
# response = rehive.admin.transactions.create_transfer(
#     user="michail",
#     amount=100,
#     currency="BCH",
#     recipient="@bob"
# )
# pp.pprint(response)



