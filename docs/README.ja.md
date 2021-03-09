# label_timer
指定されたラベルが Issue, Pull Request に付与されていた時間をはかるものです。

## 使い方
yaml の例

```yaml
name: Timer
on:
  issues:
    types:
      ['labeled', 'unlabeled']
  pull_request:
    types:
      ['labeled', 'unlabeled']
jobs:
  timer:
    runs-on: ubuntu-latest
    steps:
      - name: test_run
        uses: tbsmcd/label_timer@master
        id: test_run
        with:
          targets: '対応中, 依頼中, needs_review'
          token: ${{ secrets.GITHUB_TOKEN }}
      - name: checkout
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == '対応中' }}
        uses: actions/checkout@v2
      - name: add_time_label
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == '対応中' }}
        run: |
          pip install requests
          python .github/add_time_label.py ${{ secrets.GITHUB_TOKEN }} ${{ github.event.issue.url }} ${{ steps.test_run.outputs.sum_seconds }}
```

Issue について計測したい場合

```yaml
on:
  issues:
    types:
      ['labeled', 'unlabeled']
```

Pull Request について計測したい場合

```yaml
on:
  pull_request:
    types:
      ['labeled', 'unlabeled']
```

を指定します。もちろん Issue, Pull Request 両方についても同時に指定できます。

対象になるラベルはカンマ区切りで複数指定できます。

## どのように計測されるのか？

![スクリーンショット 2021-03-10 0 56 21](https://user-images.githubusercontent.com/174922/110499414-8affb700-813b-11eb-90a4-1e6629c414f4.png)

対象のラベルが追加されたら計測用ラベルが Issue/Pull Request に付加されます。対象のラベルが削除されたら計測用ラベルも削除され、計測結果がコメントされます。計測対象のラベルが複数回付加・削除された場合は合計時間がコメントされます。

## 結果の取得

```python
    def set_outputs(self):
        print("::set-output name=action::{}".format(self.events['action']))
        print("::set-output name=label::{}".format(self.events['label']['name']))
        if self.events['action'] == 'unlabeled':
            print("::set-output name=passed_seconds::{}".format(self.passed_seconds))
            print("::set-output name=sum_seconds::{}".format(self.passed_seconds + self.before_passed_seconds))
        return
```

アクション（labeled | unlabeled）、ラベル名、経過時間、合計の経過時間を outputs として取得できます。以下は具体例です。

```yaml
      - name: add_time_label
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == '対応中' }}
        run: |
          pip install requests
          python .github/add_time_label.py ${{ secrets.GITHUB_TOKEN }} ${{ github.event.issue.url }} ${{ steps.test_run.outputs.sum_seconds }}
```