import os
import shutil
from prompts.prompts_hamdler import PromptHandler
from utils.aoai_handler import AOAIHandler
from utils.markdown_handler import MarkdownHandler
from colorama import Fore, Style, init
import json
from datetime import datetime, timedelta
import pytz

# Windowsでも動作するように初期化
init()

with open("config.json", 'r', encoding='utf-8') as config:
    data = json.load(config)
    repo = data["repo"]
    out_repo = data["out_repo"]
    EXCLUDE_DIRS = data["EXCLUDE_DIRS"]
    translation_commit_deadline = data["translation_commit_deadline"]

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

# Gitのコミット日付をdatetimeオブジェクトに変換
def parse_git_date(git_date_str):
    return datetime.strptime(git_date_str, '%a %b %d %H:%M:%S %Y %z')

# "1 week ago" などの相対時間を現在時刻からの timedelta で引いて、datetime に変換
def parse_relative_time(relative_time_str):
    now = datetime.now(pytz.utc)  # 現在時刻（UTC）
    time_map = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(weeks=4),  # 1ヶ月を4週間と仮定
    }

    # 文字列を分解して適切な timedelta を適用
    for unit in time_map:
        if unit in relative_time_str:
            number = int(relative_time_str.split()[0])
            return now - time_map[unit] * number

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
        markdown_handler = MarkdownHandler(md_file_path)

        # 中身がない場合はスキップ
        if markdown_handler.markdown == "":
            continue

        # ファイルがすでに翻訳済みの場合はスキップ
        destination_file_path = md_file_path.replace(source_dir, destination_dir)
        destination_file = MarkdownHandler(destination_file_path)

        # すでに翻訳済みかどうかをチェックし、翻訳済みの場合かつコミットが直近ではない場合はスキップする
        if destination_file.is_translated():
            recent_commit_date = parse_git_date(markdown_handler.recent_commit_date)
            commit_deadline = parse_relative_time(translation_commit_deadline)

            # recent_commit_date が commit_deadline よりも古いなら変化がないのでスキップ
            if recent_commit_date <= commit_deadline:
                print(f"{Fore.GREEN}/----\n recent_commit_date is old and passed commit_deadline\n----/{Style.RESET_ALL}")
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

            # if "DEBUG" in os.environ:
            #     print(f"\n Hers is message: \n{messages}\n")

            # AOAI にリクエストを送信し、結果を取得
            markdown_handler.translated_content += aoai_handler.execute(messages)

        destination_file.write_content(markdown_handler.translated_content)

        # translated_contentを行ごとに分割
        lines = markdown_handler.translated_content.splitlines()
        # 最後の5行を取得して出力
        for line in lines[-5:]:
            print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")

        print(f"\nTranslated content has been written to {destination_file_path}\n----------------//\n")
