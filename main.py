import os
import shutil
import sys
from prompts.prompts_hamdler import PromptHandler
from utils.aoai_handler import AOAIHandler
from utils.markdown_handler import MarkdownHandler
from colorama import Fore, Style, init
import json

# Windowsでも動作するように初期化
init()

with open("config.json", 'r', encoding='utf-8') as config:
    data = json.load(config)
    repo = data["repo"]
    out_repo = data["out_repo"]
    EXCLUDE_DIRS = data["EXCLUDE_DIRS"]

# 絶対パスに変換
EXCLUDE_DIRS = [os.path.abspath(exclude_dir) for exclude_dir in EXCLUDE_DIRS]

def should_exclude_dir(dir_path):
    dir_path = os.path.abspath(dir_path)
    for exclude_dir in EXCLUDE_DIRS:
        if os.path.commonpath([dir_path, exclude_dir]) == exclude_dir:
            return True
    return False

def get_markdown_files(start_dir):
    markdown_files_paths = []
    for root, dirs, files in os.walk(start_dir):
        # 走査しないディレクトリを除外
        dirs[:] = [d for d in dirs if not should_exclude_dir(os.path.join(root, d))]
        for file in files:
            if file.endswith(".md"):
                # 相対パスを取得
                relative_path = os.path.relpath(os.path.join(root, file), start_dir)
                markdown_files_paths.append(os.path.join(start_dir, relative_path))
    return markdown_files_paths

if __name__ == "__main__":
    # 検索するレポジトリを指定
    repository_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), repo)
    markdown_files_paths = get_markdown_files(repository_path)

    if "DEBUG" in os.environ:
        for md_file in markdown_files_paths:
            print(md_file)

    # 対象のディレクトリをそのまま Translated フォルダを作成してコピーする。
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), repo)
    destination_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), out_repo)

    if not os.path.exists(destination_dir):
        shutil.copytree(source_dir, destination_dir)

    for md_file_path in markdown_files_paths:
    # DEBUG
    # for test in range(1):
        # md_file_path = "full path like C:/Users/username/something.md"

        markdown_handler = MarkdownHandler(md_file_path)

        # 中身がない場合はスキップ
        if markdown_handler.markdown == "":
            continue

        print(f"//----------------\nProcessing {md_file_path}")

        # # 分割処理
        markdown_handler.tokenize_as_translation()

        for section in markdown_handler.tokenized_sections:
            if section == "":
                continue

                # プロンプト生成部
            prompt_handler = PromptHandler()
            aoai_handler = AOAIHandler()

            # User Prompt に加える
            prompt_handler.add_user_prompt(section)
            # メッセージを作成
            messages = prompt_handler.create_messages()

            print(f"\n Hers is message: \n{messages}\n")
            # AOAI にリクエストを送信し、結果を取得
            markdown_handler.translated_content += aoai_handler.execute(messages)

        # md_file_path のディレクトリを ADO Wiki の repo から Translated に変更
        md_file_path = md_file_path.replace(repo, out_repo)
        with open(md_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(markdown_handler.translated_content)

        # translated_contentを行ごとに分割
        lines = markdown_handler.translated_content.splitlines()
        # 最後の5行を取得して出力
        for line in lines[-5:]:
            print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")

        print(f"\nTranslated content has been written to {md_file_path}\n----------------//\n")
