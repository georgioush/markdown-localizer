import os
import subprocess

def main():
    # Execute git update-index --assume-unchanged config.json
    try:
        subprocess.run(["git", "update-index", "--assume-unchanged", "config.json"], check=True)
        print("Successfully set config.json to assume unchanged.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()