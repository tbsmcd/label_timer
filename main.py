from os import environ
import json
from pprint import pprint

targets = [x.strip() for x in environ.get('INPUT_TARGETS').split(',')]
print(targets)

with open(environ.get('GITHUB_EVENT_PATH')) as f:
    events = json.load(f)
    pprint(events)
