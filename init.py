import os
import subprocess

def main():
    # git update-index --assume-unchanged config.json を実行
    try:
        subprocess.run(["git", "update-index", "--assume-unchanged", "config.json"], check=True)
        print("Successfully set config.json to assume unchanged.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()