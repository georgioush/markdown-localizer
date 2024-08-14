@echo off

REM 仮想環境のディレクトリ名
set VENV_DIR=venv

REM 仮想環境が既に存在するか確認
if exist %VENV_DIR% (
    echo Activating the virtual environment.
) else (
    echo Creating a new virtual environment.
    python -m venv %VENV_DIR%
    call %VENV_DIR%\Scripts\activate
    echo Installing requirements...
    pip install -r requirements.txt
)

REM 仮想環境を有効化
call %VENV_DIR%\Scripts\activate

REM init.py を実行
python init.py
