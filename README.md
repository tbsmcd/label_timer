
# label_timer
Measures how long a given label has been attached to an issue or pull request.

## Usage
yaml example

````yaml
name: Timer
on:
  issues:
    types:
      ['labeled', 'unlabeled'].
  pull_request:
    types:
      ['labeled', 'unlabeled']]
jobs:
  timer:
    runs-on: ubuntu-latest
    steps:
      - name: test_run
        uses: tbsmcd/label_timer@master
        id: test_run
        with:
          targets: 'responding, requesting, needs_review'
          token: ${{ secrets.GITHUB_TOKEN }}
      - name: checkout
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == 'responding' }}
        uses: actions/checkout@v2
      - name: add_time_label
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == 'responding' }}
        run: |
          pip install requests
          python .github/add_time_label.py ${{ secrets.GITHUB_TOKEN }} ${{ github.event.issue.url }} ${{ steps.test_run.outputs.sum_seconds }}
````

If you want to measure about an issue

```yaml
on:
  issues:
    types:
      ['labeled', 'unlabeled'].
````

If you want to measure pull requests

```yaml
on:
  pull_request:
    types:
      ['labeled', 'unlabeled'].
````

on: pull_request: types: ['labeled', 'unlabeled'] ````. Of course, you can specify this for both issues and pull requests at the same time.

You can specify multiple labels to target, separated by commas.

## How is it measured?

! [Screenshot 2021-03-10 0 56 21](https://user-images.githubusercontent.com/174922/110499414-8affb700-813b-11eb-90a4-1e6629c414f4.png)

When the target label is added, the measurement label will be added to the issue/pull request. When the target label is removed, the measurement label is also removed and the measurement result is commented. If the target label is added or removed multiple times, the total time will be commented.

## Get the results

```python
    def set_outputs(self):
        print("::set-output name=action::{}".format(self.events['action']))
        print("::set-output name=label::{}".format(self.events['label']['name']))
        if self.events['action'] == 'unlabeled':
            print("::set-output name=passed_seconds::{}".format(self.passed_seconds))
            print("::set-output name=sum_seconds::{}".format(self.passed_seconds + self.before_passed_seconds))
        return
````

You can get the action (labeled | unlabeled), label name, elapsed time, and total elapsed time as outputs. The following is a concrete example.

```yaml
      - name: add_time_label
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == 'responding' }}
        run: |
          pip install requests
          python .github/add_time_label.py ${{ secrets.GITHUB_TOKEN }} ${{ github.event.issue.url }} ${{ steps.test_run.outputs.sum_seconds }}
```
