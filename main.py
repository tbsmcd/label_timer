from os import environ
import json
import datetime
import time
from pprint import pprint

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

    def is_target(self):
        return self.events['label']['name'] in self.targets

    def add_label(self):
        # If a label with a prefix exists, do not add a new label.
        current_labels = \
            [x for x in self.events['issue']['labels'] if x['name'].startswith(self.prefix)]
        if len(current_labels) > 0:
            return
        label_to_add = self.prefix + str(int(time.time()))
        print(label_to_add)


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
