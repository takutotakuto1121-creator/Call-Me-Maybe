*This project has been created as part
of the 42 curriculum by tsugimot*
# Call Me Maybe
## Description
**Call Me Maybe**は、42cursusのMilestone3のソロ課題です。
*Constrained Decoding*を用いて、LLMの出力を指定された形式のJSONでの出力に強制するプログラムを書きます。詳細は[課題要件](docs/subject.md)を見てください。

## Instruction
以下のコマンドで実行します。
```bash
make run
```

入力ファイルの先頭１つのみのプロンプトに対する出力を標準出力に出力するには以下のコマンドで実行します。
```bash
make test
```

トークンの生成過程を標準出力に出力しながら実行するには以下のコマンドで実行します。
```bash
make animation
```

入力ファイル、出力ファイルを指定したければ以下のように実行すれば指定できます。
```bash
uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--
output <output_file>]
```

## Alhorithm explanation
### パース
パースは今更なので割愛。コードを見れば分かります。`pydantic`, `json`を用いてバリデーションをしています。

### LLMを用いた実装
まず、Small_LLM_Modelを用いて、普段のように文章を生成させる方法を考えます。[こちら](docs/simple_llm.md)を参照してください。

### Constrained Decoding
先ほど作成したSimpleLLMを改造して指定したJSONのフォーマットに従わせる方法を考えます。[こちら](docs/constrained.md)を参照してください。

次に文字列が課題要件で指定されたJSONフォーマットに適しているかどうかを確認するチェッカーを作成します。[こちら](docs/json_checker.md)

## Resouces
### AI Usage
コードは手書きて書いています。
flake8, mypyエラーの解消のためにAIを用いました。

### Resouces
あとでかく

## その他
その他のおまけ情報は[こちら](docs/others.md)へ。