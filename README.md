# label_timer
[日本語](https://github.com/tbsmcd/label_timer/blob/master/docs/README.ja.md)

Measures how long a given label has been attached to an issue or pull request.

## Usage
example.yml

```yaml
name: Timer
on:
  # For pull request labels
  issues:
    types:
      ['labeled', 'unlabeled'].
  # For pull request labels
  pull_request:
    types:
      ['labeled', 'unlabeled']
jobs:
  timer:
    runs-on: ubuntu-latest
    steps:
      - name: test_run
        uses: tbsmcd/label_timer@v2.2
        id: test_run
        with:
          # You can specify multiple labels separated by commas.
          targets: 'responding, requesting, needs_review'
          token: ${{ secrets.GITHUB_TOKEN }}
      # If you want to use the measurement results in later steps
      - name: checkout
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == 'responding' }}
        uses: actions/checkout@v2
      - name: add_time_label
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == 'responding' }}
        # outputs can be obtained as the following variables.
        #
        # If `github.event.action == labeled`.
        # ${ steps.test_run.outputs.url }} URL of the issue or pull request that was targeted.
        #
        # If `github.event.action == unlabeled`.
        # ${ steps.test_run.outputs.url }} URL of the issue or pull request that was targeted
        # ${ steps.test_run.outputs.passed_seconds }} Number of seconds between label assignment and removal
        # ${ steps.test_run.outputs.sum_seconds }} Number of seconds between labeling and deletion (total)
        run: |
          pip install requests
          python .github/example.py ${{ secrets.GITHUB_TOKEN }} ${{ github.event.issue.url }} ${{ steps.test_run.outputs.sum_seconds }}
```

## How is it measured?

![screenshot 2021-03-10 0 56 21](https://user-images.githubusercontent.com/174922/110499414-8affb700-813b-11eb-90a4-1e6629c414f4.png)

When the target label is added, the measurement label will be added to the issue/pull request. When the target label is removed, the measurement label is also removed and the measurement result is commented. If the target label is added or removed multiple times, the total time will be commented.

## Get the result

In the following steps and jobs, you can get URL of issue/pull request, the number of seconds between when the label was added and when it was removed, and the total time.

## Usage example

- Measure the lead time from review request to review completion for pull requests.
- Measure the lead time from request to completion for Ops tasks.

The results can be referenced later in steps / jobs as outputs variables, so you can save them to BigQuery or a spreadsheet.