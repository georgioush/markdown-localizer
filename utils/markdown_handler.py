import os
import re
import sys
import chardet
import subprocess
from utils.token_counter import TokenCounter
from colorama import Fore, Style, init

# Initialize for Windows compatibility
init()

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory to the module search path
sys.path.append(os.path.join(current_dir, '..'))

# Regular expressions to capture header sections
HEADER_PATTERNS = [
    (1, r'(?:^|\n)\s*(#\s*.+?)(?=(?:\n\s*#|\n\Z|\Z))'),
    (2, r'(?:^|\n)\s*(##\s*.+?)(?=(?:\n\s*##|\n\Z|\Z))'),
    (3, r'(?:^|\n)\s*(###\s*.+?)(?=(?:\n\s*###|\n\Z|\Z))'),
    (4, r'(?:^|\n)\s*(####\s*.+?)(?=(?:\n\s*####|\n\Z|\Z))'),
    (5, r'(?:^|\n)\s*(#####\s*.+?)(?=(?:\n\s*#####|\n\Z|\Z))'),
]

MAX_TOKENS = 2048

TRANSLATION_MARKER = "<!-- TRANSLATED -->"

class MarkdownHandler:
    def __init__(self, markdown_path):
        self.markdown_path = os.path.normpath(markdown_path)

        # Open the file in binary mode and detect encoding
        with open(self.markdown_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']

        # Retry if detected encoding is not UTF-8 or confidence is low
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
            # Use git log to get the most recent commit date for a specific file
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%cd', '--', self.markdown_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(self.markdown_path)
            )
            if result.returncode == 0:
                # Return the commit date
                return result.stdout.strip()
            else:
                # Display error message
                print(f"Error retrieving recent commit: {result.stderr}")
                return None
        except Exception as e:
            print(f"An error occurred while retrieving the recent commit date: {e}")
            return None

    def is_translated(self):
        # Check if the first line of self.markdown contains <!-- TRANSLATED -->
        return self.markdown.startswith(TRANSLATION_MARKER)

    def write_content(self, content):
        # Open the file in binary mode and detect encoding
        with open(self.markdown_path, 'w', encoding='utf-8') as file:
            file.write(TRANSLATION_MARKER + "\n")
            file.write(content)
        
    def tokenize_as_translation(self):
        token_counter = TokenCounter()

        # If the entire file is within the token size limit, return it as is
        if MAX_TOKENS > token_counter.count_tokens(self.markdown):
            self.tokenized_sections = [self.markdown]
            print("Section Size:", f"{token_counter.count_tokens(self.markdown)}")
            return 
        
        # If the file exceeds the token size limit, split it into sections by headers
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
        # Since section is a part of markdown, first count the number of lines
        lines = section.split('\n')
        line_count = len(lines)

        # Calculate the number of sections by dividing the token count of the section by max_tokens, rounding up
        section_num = -(-token_counter.count_tokens(section) // MAX_TOKENS)

        # Determine the number of lines per split section by dividing line_count by section_num, subtracting one line for safety
        split_line_count = line_count // section_num - 1 

        # Create split sections by taking split_line_count lines at a time from the initial line count
        tokenized_sections = []
        for i in range(section_num):
            start = i * split_line_count
            end = (i + 1) * split_line_count
            tokenized_sections.append("\n".join(lines[start:end]))

        return tokenized_sections