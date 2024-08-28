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


## Enabling Long Paths in Windows
Starting from Windows 10 (version 1607 or later), you can enable long path support to remove the 260-character limitation (MAX_PATH) by modifying the system registry. By default, Windows does not allow file paths longer than 260 characters. However, you can enable support for longer paths (up to 32,767 characters) using the following steps:

### Method 1: Modify Registry to Enable Long Paths System-wide
Open the Registry Editor:

Press Win + R, type regedit, and press Enter. This will open the Windows Registry Editor.
Navigate to the Long Path Support Key:

In the Registry Editor, navigate to the following path:
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem

Enable Long Paths:

Look for a DWORD (32-bit) entry named LongPathsEnabled.
If the LongPathsEnabled entry does not exist, right-click on the FileSystem folder, select New > DWORD (32-bit) Value, and name it LongPathsEnabled.
Double-click on LongPathsEnabled, set the value to 1, and click OK.

## Enabling Long Paths in git

git config --system core.longpaths true