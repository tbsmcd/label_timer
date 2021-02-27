from os import environ
import json
import datetime
import time
from pprint import pprint
import requests

# with open(environ.get('GITHUB_EVENT_PATH')) as f:
#     events = json.load(f)
#     action = events['action']
#     label = events['label']['name']
#     print(action)
#     print(label)
#     pprint(events)


class Label:
    def __init__(self, events, targets):
        self.events = events
        self.targets = targets
        self.prefix = 'label_timer_' + self.events['label']['name'] + '_'
        self.headers = {'Authorization': 'token %s' % environ.get('INPUT_TOKEN')}

    def is_target(self):
        return self.events['label']['name'] in self.targets

    def add_label(self):
        # If a label with a prefix exists, do not add a new label.
        current_labels = [x['name'] for x in self.events['issue']['labels']]
        if len([x for x in current_labels if x.startswith(self.prefix)]) > 0:
            return
        label_to_add = self.prefix + str(int(time.time()))
        api_url = self.events['issue']['url'] + '/labels'
        payload = {'labels': [label_to_add]}
        requests.post(api_url, headers=self.headers, data=json.dumps(payload))



def main():
    targets = [x.strip() for x in environ.get('INPUT_TARGETS').split(',')]
    with open(environ.get('GITHUB_EVENT_PATH')) as f:
        events = json.load(f)
        label = Label(events, targets)
        if label.is_target() is False:
            return
        if events['action'] == 'labeled':
            label.add_label()
        elif events['action'] == 'unlabeled':
            pass


if __name__ == '__main__':
    main()
