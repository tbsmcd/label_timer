from os import environ
import json
import datetime
import time
from pprint import pprint
import requests
import urllib.parse


class Label:
    def __init__(self, events, targets):
        self.events = events
        self.targets = targets
        # TODO: issue 特有にする
        self.prefix = 'label_timer_' + self.events['label']['name'] +\
                      '_' + self.events['issue']['number']
        self.headers = {'Authorization': 'token %s' % environ.get('INPUT_TOKEN')}
        self.current_labels = [x['name'] for x in self.events['issue']['labels']]
        self.passed_seconds = 0

    def is_target(self):
        return self.events['label']['name'] in self.targets

    def add(self):
        # If a label with a prefix exists, do not add a new label.
        if len([x for x in self.current_labels if x.startswith(self.prefix)]) > 0:
            return
        label_to_add = self.prefix + str(int(time.time()))
        api_url = self.events['issue']['url'] + '/labels'
        payload = {'labels': [label_to_add]}
        r = requests.post(api_url, headers=self.headers, data=json.dumps(payload))
        if r.status_code != 200:
            print('Add label: status_code {}'.format(r.status_code))
            exit
        return

    def remove(self):
        # List of labels with prefix
        timer_labels = [x for x in self.current_labels if x.startswith(self.prefix)]
        if len(timer_labels) == 0:
            return
        timer_labels.sort()
        start_time = int(timer_labels[0].replace(self.prefix, ''))
        self.passed_seconds = time.time() - start_time
        # print('::set-output name=PASSED_SECONDS::{}'.format(self.passed_seconds))
        api_base_url = self.events['issue']['url'] + '/labels/{}'
        for label in timer_labels:
            # api_url = api_base_url.format(urllib.parse.quote(label))
            # r = requests.delete(api_url, headers=self.headers)
            # print('Remove label {0}: status code {1}'.format(label, r.status_code))
            # TODO: API からラベルを消去
            api_url = self.events['repository']['labels_url']\
                .replace('{/name}', '/' + urllib.parse.quote(label))
            r = requests.delete(api_url, headers=self.headers)
            print('Remove label {0}: status code {1}'.format(label, r.status_code))
        return

    def comment(self):
        body = 'Label {0} passed time: {1}'.\
            format(self.events['label']['name'], str(datetime.timedelta(seconds=self.passed_seconds)))
        api_url = self.events['issue']['url'] + '/comments'
        payload = {'body': body}
        r = requests.post(api_url, headers=self.headers, data=json.dumps(payload))
        if r.status_code != 200:
            print('Add comment: status_code {}'.format(r.status_code))
            exit
        return

    def delete(self):
        # TODO: API からラベル一覧を取得して消去
        pass


def main():
    targets = [x.strip() for x in environ.get('INPUT_TARGETS').split(',')]
    with open(environ.get('GITHUB_EVENT_PATH')) as f:
        events = json.load(f)
        label = Label(events, targets)
        if label.is_target() is False:
            return
        if events['action'] == 'labeled':
            label.add()
        elif events['action'] == 'unlabeled':
            label.remove()
            print(environ.get('INPUT_COMMENT'))
            if environ.get('INPUT_COMMENT') == 'true':
                label.comment()


if __name__ == '__main__':
    main()
