import os
import shutil
from shutil import ignore_patterns
from prompts.prompts_hamdler import PromptHandler
from utils.aoai_handler import AOAIHandler
from utils.markdown_handler import MarkdownHandler
from colorama import Fore, Style, init
import json
from datetime import datetime, timedelta
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Initialize for Windows compatibility
init()

with open("config.json", 'r', encoding='utf-8') as config:
    data = json.load(config)
    repo = data["repo"]
    out_repo = data["out_repo"]
    EXCLUDE_DIRS = data["EXCLUDE_DIRS"]
    translation_commit_deadline = data["translation_commit_deadline"]

# Convert to absolute paths
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
        # Exclude directories that should not be scanned
        dirs[:] = [d for d in dirs if not should_exclude_dir(os.path.join(root, d))]
        for file in files:
            if file.endswith(".md"):
                # Get relative path
                relative_path = os.path.relpath(os.path.join(root, file), start_dir)
                markdown_files_paths.append(os.path.join(start_dir, relative_path))
    return markdown_files_paths

# Convert Git commit date to datetime object
def parse_git_date(git_date_str):
    return datetime.strptime(git_date_str, '%a %b %d %H:%M:%S %Y %z')

# Convert relative time like "1 week ago" to datetime by subtracting timedelta from now
def parse_relative_time(relative_time_str):
    now = datetime.now(pytz.utc)  # Current time (UTC)
    time_map = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(weeks=4),  # Assume 1 month as 4 weeks
    }

    # Split the string and apply appropriate timedelta
    for unit in time_map:
        if unit in relative_time_str:
            number = int(relative_time_str.split()[0])
            return now - time_map[unit] * number

def process_markdown_file(md_file_path, source_dir, destination_dir):
    try:
        markdown_handler = MarkdownHandler(md_file_path)
    except Exception as e:
        print(f"Error reading {md_file_path}: {e}")
        return

    # Skip if the content is empty
    if markdown_handler.markdown == "":
        return

    # Skip if the file is already translated
    destination_file_path = md_file_path.replace(source_dir, destination_dir)
    destination_file = MarkdownHandler(destination_file_path)

    # Check if already translated and skip if the recent commit is not recent
    if destination_file.is_translated():
        recent_commit_date = parse_git_date(markdown_handler.recent_commit_date)
        commit_deadline = parse_relative_time(translation_commit_deadline)

        # Skip if recent_commit_date is older than commit_deadline
        if recent_commit_date <= commit_deadline:
            print(f"{Fore.GREEN}/----\n The latest commit date is not recent and is outside the translation commit deadline\n----/{Style.RESET_ALL}")
            return

    print(f"//----------------\nProcessing {md_file_path}")

    # Tokenize for translation
    markdown_handler.tokenize_as_translation()

    for section in markdown_handler.tokenized_sections:
        if section == "":
            continue

        # Prompt generation
        prompt_handler = PromptHandler()
        aoai_handler = AOAIHandler()

        # Add to User Prompt
        prompt_handler.add_user_prompt(section)
        # Create messages
        messages = prompt_handler.create_messages()

        # Send request to AOAI and get the result with retry and backoff strategy
        retry_count = 0
        max_retries = 10
        backoff_factor = 2

        while retry_count < max_retries:
            try:
                response = aoai_handler.execute(messages)
                if response is None:
                    print(f"Received None response from AOAIHandler for {md_file_path}")
                else:
                    markdown_handler.translated_content += response
                break
            except Exception as e:
                retry_count += 1
                wait_time = min(2 * retry_count, 10)  # Start with 2 minutes, then 3, 4, 5, up to 10 minutes
                print(f"Error: {e}. Retrying in {wait_time} minutes...")
                time.sleep(wait_time * 60)  # Convert minutes to seconds
                if retry_count == max_retries:
                    print(f"Failed to process {md_file_path} after {max_retries} retries.")
                    return

    destination_file.write_content(markdown_handler.translated_content)

    # Split translated_content by lines
    lines = markdown_handler.translated_content.splitlines()
    # Get and print the last 5 lines
    for line in lines[-5:]:
        print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")

    print(f"\nTranslated content has been written to {destination_file_path}\n----------------//\n")

if __name__ == "__main__":
    # Specify the repository to search
    repository_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), repo)
    markdown_files_paths = get_markdown_files(repository_path)

    if "DEBUG" in os.environ:
        for md_file in markdown_files_paths:
            print(md_file)

    print(f"File total: {len(markdown_files_paths)}")

    # Copy the target directory as it is to create a Translated folder.
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), repo)
    destination_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), out_repo)

    # Check whether files on markdown_files_paths exist
    for md_file_path in markdown_files_paths:
        if not os.path.exists(md_file_path):
            print(f"{Fore.RED}File not found: {md_file_path}{Style.RESET_ALL}")


    if not os.path.exists(destination_dir):
        shutil.copytree(source_dir, destination_dir, ignore=ignore_patterns('.git'))

    # Ensure the copy operation is complete before proceeding
    while not os.path.exists(destination_dir):
        time.sleep(1)

    # Use ThreadPoolExecutor to process files in parallel with a maximum of 5 threads
    max_workers = 100
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_markdown_file, md_file_path, source_dir, destination_dir) for md_file_path in markdown_files_paths]
        for future in as_completed(futures):
            future.result()  # Wait for all futures to complete