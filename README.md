## Steps

1. **Run Initialization Script**
   - Execute `init.py` to perform initial setup.

2. **Clone ADO Wiki**
   - Clone the target ADO Wiki.

3. **Modify Configuration File**
   - Edit the contents of `config.json`.
     - Specifically, configure which directories should not be translated.
     - Also, specify the name of the ADO Wiki as `original`.

4. **Edit Prompt Settings**
   - Edit `prompt_selector.json` under the `prompts` directory.
     - (Optional) Create a folder for your language (e.g., `ja-jp`).
       - Place `system_prompt.md` and `user_prompt.md` under that folder.
       - Update the path in `prompt_selector.json`.
     - If the current prompts are fine, set `language` to your language.

5. **Run Main Script**
   - Execute `main.py`.
     - Ensure the following environment variables are properly set:
       - `AZURE_OPENAI_API_KEY`
       - `AZURE_OPENAI_ENDPOINT`
       - `AZURE_OPENAI_DEPLOYMENT_NAME`
       - `AZURE_OPENAI_API_VERSION`