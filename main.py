from os import environ
import json
from pprint import pprint

targets = [x.strip() for x in environ.get('INPUT_TARGETS').split(',')]
print(targets)
events = json.load(environ.get('GITHUB_EVENT_PATH'))
pprint(events)