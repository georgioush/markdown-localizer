@echo off

REM Directory name for the virtual environment
set VENV_DIR=venv

REM Check if the virtual environment already exists
if exist %VENV_DIR% (
    echo Activating the virtual environment.
) else (
    echo Creating a new virtual environment.
    python -m venv %VENV_DIR%
    call %VENV_DIR%\Scripts\activate
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate

REM Execute init.py
python init.py