@echo off

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements
pip install -r requirements.txt

echo Virtual environment created and dependencies installed!
echo To activate the virtual environment, run: venv\Scripts\activate 