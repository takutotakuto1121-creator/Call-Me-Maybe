# その他
## Design decisions
- バリデーションには`pydantic`, `json`を使用しました。使い慣れているからです。
- ConstrainedLLMの`decode`は最初と最後の１回のみにしました。速度が速くなるからです。
- JsonCheckerにはスタックは使用していません。JSONのフォーマットが詳しく指定されていたため、ネストは考える必要がなかったからです。

## Performance analysis
- Accuracy: かなり正確です。90%以上は正確な出力が返ってきます。
- Speed: 課題要件の5分以内はクリアしています。ただ、まだまだ改善の余地はあります。
- Reliability: パースを完璧に行っているのでクラッシュはしません。エラーハンドリングも厳しく行っています。

## Callenges faced
- [ConstrainedLLM](constrained.md)を作成する際に、実行速度が極めて遅くなる課題に直面しました。`decode`を何回も行っていたことと、`check_json`の際に全てのトークンに対してチェックを行っていたことが主な原因でした。`decode`を最初と最後のみにし、トークンのチェックは確率が高い順番にしていくようにして実行速度を早くしました。
- [JsonChecker](json_checker.md)を作成する際に、最初はまず100%正しいJSONの出力になるようにチェックし、その後に指定した形式化をチェックしようとしました。なんなら形式も自由に指定できるようにしようとしていました。ただこの実装が現時点の力では難しかったので簡略化し、課題要件を満たすのみの実装にすることにより解決しました。もう少し力をつけてかたその実装にも挑戦したいです。

## Testing stratgy
`input/function_calling_tests.json`の最初のプロンプト、`input/function_definition.json`を自分の好きなように変更し、以下のコマンドで実行し、出力を確かめることによりテストができます。

```bash
make test
```

## Example Usage
inputディレクトリのファイルはデフォルトのままで以下のコマンドで実行してください。
```bash
make run
```