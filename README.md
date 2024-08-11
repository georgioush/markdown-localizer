## 手順

1. **初期化スクリプトの実行**
   - `init.py` を実行して初期設定を行います。

2. **ADO Wiki のクローン**
   - 対象となる ADO Wiki をクローンします。

3. **設定ファイルの修正**
   - `config.json` の内容を修正します。
     - 具体的には、どのディレクトリを翻訳対象にしないかなどを設定します。
     - また、ADO Wiki の名前を `original` として指定します。

4. **プロンプト設定の編集**
   - `prompts` 配下の `prompt_selector.json` を編集します。
     - (オプション) 自分の国の言語に合わせてフォルダを作成します (例: `ja-jp`)。
       - その配下に `system_prompt.md` および `user_prompt.md` を配置します。
       - `prompt_selector.json` のパスを修正します。
     - 現状のプロンプトで問題ない場合は、`language` を自分の国の言語に設定します。

5. **メインスクリプトの実行**
   - `main.py` を実行します。
     - なお、以下の環境変数が正常に設定されていることを前提としています。
       - `AZURE_OPENAI_API_KEY`
       - `AZURE_OPENAI_ENDPOINT`
       - `AZURE_OPENAI_DEPLOYMENT_NAME`
       - `AZURE_OPENAI_API_VERSION`