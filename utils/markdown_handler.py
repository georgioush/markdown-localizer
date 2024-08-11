import os
import re
import sys
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

class MarkdownHandler:
    def __init__(self, markdown_path):
        self.markdown_path = os.path.normpath(markdown_path)
    
        try:
            with open(self.markdown_path, 'r', encoding='utf-8') as file:
                 self.markdown = file.read()
        except FileNotFoundError:
            raise Exception(f"Failed to open {self.markdown_path} Please make sure the file exists.")

        self.tokenized_sections = []
        self.translated_content = ""
        self.summarized_content = ""

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