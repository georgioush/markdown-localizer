import os
import re
import sys
import chardet
import subprocess
from utils.token_counter import TokenCounter
from colorama import Fore, Style, init

# Windowsでも動作するように初期化
init()

# 現在のファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
# 親ディレクトリをモジュール検索パスに追加
sys.path.append(os.path.join(current_dir, '..'))

# ヘッダー部を捉えるための正規表現 
HEADER_PATTERNS = [
    (1, r'(?:^|\n)\s*(#\s*.+?)(?=(?:\n\s*#|\n\Z|\Z))'),
    (2, r'(?:^|\n)\s*(##\s*.+?)(?=(?:\n\s*##|\n\Z|\Z))'),
    (3, r'(?:^|\n)\s*(###\s*.+?)(?=(?:\n\s*###|\n\Z|\Z))'),
    (4, r'(?:^|\n)\s*(####\s*.+?)(?=(?:\n\s*####|\n\Z|\Z))'),
    (5, r'(?:^|\n)\s*(#####\s*.+?)(?=(?:\n\s*#####|\n\Z|\Z))'),
]

MAX_TOKENS = 2048

TRANSALTION_MARKER = "<!-- TRANSLATED -->"

class MarkdownHandler:
    def __init__(self, markdown_path):
        self.markdown_path = os.path.normpath(markdown_path)
    
class MarkdownHandler:
    def __init__(self, markdown_path):
        self.markdown_path = os.path.normpath(markdown_path)

        # ファイルをバイナリモードで開き、エンコーディングを検出
        with open(self.markdown_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']

        # 検出されたエンコーディングが UTF-8 でないか、信頼性が低い場合は再試行
        if encoding != 'utf-8' or confidence < 0.5:
            print(f"Detected encoding: {encoding} (Confidence: {confidence})")
            print(f"Converting {self.markdown_path} from {encoding} to UTF-8.")
            try:
                # Try to read the file with detected encoding
                with open(self.markdown_path, 'r', encoding=encoding, errors='replace') as file:
                    content = file.read()
                
                # Now encode the content to UTF-8 and rewrite the file
                with open(self.markdown_path, 'w', encoding='utf-8', errors='replace') as file:
                    file.write(content)
                
                self.markdown = content

            except UnicodeDecodeError:
                print(f"Error decoding with {encoding}, trying fallback encoding 'utf-8'.")
                with open(self.markdown_path, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                
                # Re-write the file in UTF-8
                with open(self.markdown_path, 'w', encoding='utf-8', errors='replace') as file:
                    file.write(content)
                
                self.markdown = content
        else:
            # If UTF-8 was correctly detected
            with open(self.markdown_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
            self.markdown = content

        self.tokenized_sections = []
        self.translated_content = ""
        self.summarized_content = ""
        self.recent_commit_date = self.check_recent_commit()

    def check_recent_commit(self):
        try:
            # git log を使って、特定のファイルの最も直近のコミット日時を取得する
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%cd', '--', self.markdown_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(self.markdown_path)
            )
            if result.returncode == 0:
                # コミット日時を返す
                return result.stdout.strip()
            else:
                # エラーメッセージを表示
                print(f"Error retrieving recent commit: {result.stderr}")
                return None
        except Exception as e:
            print(f"An error occurred while retrieving the recent commit date: {e}")
            return None

    def is_translated(self):
        # self.markdown の最初の行に <!-- TRANSLATED --> が含まれているかを確認する
        return self.markdown.startswith(TRANSALTION_MARKER)

    def write_content(self, content):
        # ファイルをバイナリモードで開き、エンコーディングを検出
        with open(self.markdown_path, 'w', encoding='utf-8') as file:

            file.write(TRANSALTION_MARKER + "\n")
            file.write(content)
        
    def tokenize_as_translation(self):
        token_counter = TokenCounter()

        # もしファイル自体が Token サイズ以下ならそのまま返して処理をさせる。
        if MAX_TOKENS > token_counter.count_tokens(self.markdown):
            self.tokenized_sections = [self.markdown]
            print("Section Size:", f"{token_counter.count_tokens(self.markdown)}")
            return 
        
        # もしファイルが Token サイズを超えている場合、ヘッダーでセクションに分割して処理をさせる。
        level = 0 
        pattern = HEADER_PATTERNS[level][1]

        sections = re.split(pattern, self.markdown, flags=re.DOTALL)
                
        for section in sections:
            if section.strip():
                print("Section Size:", f"{token_counter.count_tokens(section)}")

        for section in sections:
            if section.strip():
                self.tokenized_sections.extend(self.tokenize_section(section))

    def tokenize_section(self, section, level=1):
        token_counter = TokenCounter()

        if token_counter.count_tokens(section) <= MAX_TOKENS:
            return [section]

        if (level + 2) > len(HEADER_PATTERNS) + 1:
            # If we have reached the maximum header depth, split the section by rows
            return self.split_large_section(section)

        tokenized_sections = []
        pattern = HEADER_PATTERNS[level][1]
        sub_sections = re.split(pattern, section, flags=re.DOTALL)

        for sub_section in sub_sections:
            if sub_section.strip():
                print("Header Level:", f"{level + 2}", "Section Size:", f"{token_counter.count_tokens(sub_section)}")
                tokenized_sections.extend(self.tokenize_section(sub_section, level + 1))

        return tokenized_sections

    def split_large_section(self, section):
        
        print(f"{Fore.RED}/---\n LARGE SECTION DETECTED\nSplitting large section\n---/{Style.RESET_ALL}")

        token_counter = TokenCounter()
        # section は markdown の一部なので、まずは行数を数える
        lines = section.split('\n')
        line_count = len(lines)

        # section のトークン数を max_tokens で割った商を求める なお、端数を切り上げた自然数にする
        section_num = -(-token_counter.count_tokens(section) // MAX_TOKENS)

        # line_count を section_num で割り、分割セクションの行数を決定する 念の為行数を 1 つ減らす
        split_line_count = line_count // section_num - 1 

        # 最初の行数から split_line_count ずつ取り出して、分割セクションを作成する
        tokenized_sections = []
        for i in range(section_num):
            start = i * split_line_count
            end = (i + 1) * split_line_count
            tokenized_sections.append("\n".join(lines[start:end]))

        return tokenized_sections