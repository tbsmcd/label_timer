# label_timer
指定されたラベルが Issue, Pull Request に付与されていた時間をはかるものです。

## 使い方
example.yml

```yaml
name: Timer
on:
  # Issue のラベルを対象とする場合
  issues:
    types:
      ['labeled', 'unlabeled']
  # Pull Request のラベルを対象とする場合
  pull_request:
    types:
      ['labeled', 'unlabeled']
jobs:
  timer:
    runs-on: ubuntu-latest
    steps:
      - name: test_run
        uses: tbsmcd/label_timer@v2.1
        id: test_run
        with:
          # ラベルはカンマ区切りで複数指定できます。
          targets: '対応中, 依頼中, needs_review'
          token: ${{ secrets.GITHUB_TOKEN }}
      # 計測結果を後の steps で利用したい場合
      - name: checkout
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == '対応中' }}
        uses: actions/checkout@v2
      - name: add_time_label
        if: ${{ github.event.action == 'unlabeled' && github.event.label.name == '対応中' }}
        # outputs は以下の変数として取得できます。
        # `github.event.action == labeled` の場合
        # ${{ steps.test_run.outputs.action }} labeled or unlabeled
        # ${{ steps.test_run.outputs.label }} 対象になったラベル
        # ${{ steps.test_run.outputs.url }} 対象になった Issue or Pull Request の URL
        # `github.event.action == unlabeled` の場合
        # ${{ steps.test_run.outputs.action }} labeled or unlabeled
        # ${{ steps.test_run.outputs.label }} 対象になったラベル
        # ${{ steps.test_run.outputs.url }} 対象になった Issue or Pull Request の URL
        # ${{ steps.test_run.outputs.passed_seconds }} ラベルが付与されてから削除されるまでの秒数
        # ${{ steps.test_run.outputs.sum_seconds }} ラベルが付与されてから削除されるまでの秒数（合計）
        run: |
          pip install requests
          python .github/example.py ${{ secrets.GITHUB_TOKEN }} ${{ github.event.issue.url }} ${{ steps.test_run.outputs.sum_seconds }}
```

## どのように計測されるのか？

![スクリーンショット 2021-03-10 0 56 21](https://user-images.githubusercontent.com/174922/110499414-8affb700-813b-11eb-90a4-1e6629c414f4.png)

対象のラベルが追加されたら計測用ラベルが Issue/Pull Request に付加されます。対象のラベルが削除されたら計測用ラベルも削除され、計測結果がコメントされます。計測対象のラベルが複数回付加・削除された場合は合計時間がコメントされます。

## 結果の取得

後の steps, jobs で `labeled or unlabeled`、ラベル名、ラベルが付与されてから削除されるまでの秒数、その合計が取得できます。

## 利用例

- Pull Request においてレビュー依頼からレビューが完了するまでにかかったリードタイムを計測
- Ops 業務において依頼から完了までにかかったリードタイムを計測

計測結果を outputs 変数として後の steps / jobs で参照できるので、これらを BigQuery やスプレッドシートに保存することができます。