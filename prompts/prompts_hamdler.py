import json
import os

class PromptHandler:
    def __init__(self):

        file = "prompt_selector.json"
        try:
            json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
            with open(json_file_path) as f:
                data = json.load(f)

        except FileNotFoundError:
            raise Exception(f"Failed to open {file} Please make sure the file exists.")

        self.language = data["language"]

        # Get the directory path of the json_file
        json_dir = os.path.dirname(json_file_path)
        system_prompt_path = data['system']
        user_prompt_path = data['user']

        try:
            system_prompt_file_path = os.path.join(json_dir, system_prompt_path)
            with open(system_prompt_file_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            raise Exception(f"Failed to open {system_prompt_file_path} Please make sure the file exists.")

        try:
            user_prompt_file_path = os.path.join(json_dir, user_prompt_path)
            with open(user_prompt_file_path, "r", encoding="utf-8") as f:
                
                self.user_prompt = f"Please translate the following content into\n\n{self.language}\n\n"
                self.user_prompt += f.read()
        except FileNotFoundError:
            raise Exception(f"Failed to open {user_prompt_file_path} Please make sure the file exists.")


    def add_user_prompt(self, prompt):
        self.user_prompt += prompt

    def add_system_prompt(self, prompt):
        self.system_prompt += prompt

    def create_messages(self):
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]

if __name__ == "__main__":

    prompt_handler = PromptHandler()
    
    # Print the prompts for verification
    print("//---\nSystem Prompt:\n---//")
    print(prompt_handler.system_prompt)
    print("//---\nUser Prompt:\n---//")
    print(prompt_handler.user_prompt)