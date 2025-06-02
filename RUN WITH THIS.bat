@echo off

title unnamed api

SETLOCAL

REM set path to virtual environment
SET VENV_DIR=.venv
SET VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat

REM check if venv exists
if not exists "%VENV_DIR%" (
	echo creating virtual environment...
	python -m venv %VENV_DIR%
)

REM activate venv
call "%VENV_ACTIVATE%"

RME install requirements
pip install -r req.txt

REM run api
uvicorn main:app

ENDLOCAL

pause