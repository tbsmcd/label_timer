from os import environ

targets = [x.strip() for x in environ.get('INPUT_TARGETS').split(',')]
print(targets)
print(environ.get('GITHUB_EVENT_NAME'))
print(environ.get('GITHUB_EVENT_PATH'))
