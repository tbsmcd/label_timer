from os import environ

targets = [x.strip() for x in environ.get('INPUT_TARGETS')]
print(targets)
