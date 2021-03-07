from os import environ
import re
import json
import datetime
import time
from pprint import pprint
import requests
import urllib.parse


class Label:
    def __init__(self, events: dict):
        self.events = events
        self.prefix = 'label_timer_{0}_{1}::'.format(self.events['label']['name'], self.events['issue']['number'])
        self.headers = {'Authorization': 'token %s' % environ.get('INPUT_TOKEN')}
        self.current_labels = [x['name'] for x in self.events['issue']['labels']]
        self.passed_seconds = 0
        self.before_passed_seconds = 0

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
        for label in timer_labels:
            api_url = self.events['repository']['labels_url']\
                .replace('{/name}', '/' + urllib.parse.quote(label))
            r = requests.delete(api_url, headers=self.headers)
            print('Remove label {0}: status code {1}'.format(label, r.status_code))
        return

    def comment(self):
        self.__set_before_passed_seconds()
        delta = re.sub(r'\.[0-9]*$', '', str(datetime.timedelta(seconds=self.passed_seconds)))
        total_delta = re.sub(r'\.[0-9]*$', '',
                             str(datetime.timedelta(seconds=self.before_passed_seconds + self.passed_seconds)))
        body = 'Label {0} passed time: {1}\n(seconds: {2})\nTotal time: {3}'.\
            format(self.events['label']['name'], delta, int(self.passed_seconds), total_delta)
        api_url = self.events['issue']['url'] + '/comments'
        payload = {'body': body}
        r = requests.post(api_url, headers=self.headers, data=json.dumps(payload))
        if r.status_code != 200:
            print('Add comment: status_code {}'.format(r.status_code))
            exit
        return

    def get_outputs(self):
        outputs = {
            'action': self.events['action'],
            'label': self.events['label']['name']
        }
        if outputs['action'] == 'labeled':
            outputs['passed_seconds'] = self.passed_seconds
            outputs['sum_seconds'] = self.passed_seconds + self.before_passed_seconds
        return outputs

    def __set_before_passed_seconds(self):
        sum_seconds = 0
        reg = re.compile(r'Label {} passed time: .+\n\(seconds: ([0-9]+)\)'.format(self.events['label']['name']))
        api_base_url = self.events['issue']['comments_url']
        for i in range(int(self.events['issue']['comments']/100) + 1):
            page = i + 1
            api_url = api_base_url + '?per_page=100&page={}'.format(page)
            print(api_url)
            r = requests.get(api_url, headers=self.headers)
            print('Get comments list, URL:{0} status_code{1}'.format(api_url, r.status_code))
            if r.status_code == 200:
                for comment in r.json():
                    if comment['user']['login'] == 'github-actions[bot]' and reg.match(comment['body']):
                        sum_seconds += int(reg.match(comment['body']).group(1))
        self.before_passed_seconds = sum_seconds
        return


def main():
    targets = [x.strip() for x in environ.get('INPUT_TARGETS').split(',')]
    with open(environ.get('GITHUB_EVENT_PATH')) as f:
        events = json.load(f)
        label = Label(events)
        if events['label']['name'] not in targets:
            return
        if events['action'] == 'labeled':
            label.add()
        elif events['action'] == 'unlabeled':
            label.remove()
            if environ.get('INPUT_COMMENT') == 'true':
                label.comment()
        print("::set-output name=results::hoge")
        print("{}".format(json.dumps(label.get_outputs())))
        # print("::set-output name=results::{}".format(json.dumps(label.get_outputs())))


if __name__ == '__main__':
    main()
