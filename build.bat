@echo off
set "VENV_NAME=.venv"
set "BUILD_LOGS=.build_logs"
set "SCRIPTS=.\%VENV_NAME%\Scripts"
set "PY=%SCRIPTS%\python.exe"
set "PYI=%SCRIPTS%\pyinstaller.exe"
set "SPEC_FILE=build.spec"

echo CREATE VENV ^> %BUILD_LOGS%\venv_log.txt
call python -m venv %VENV_NAME% > "%BUILD_LOGS%\venv_log.txt"

echo CREATE UPGRADE PIP ^> %BUILD_LOGS%\pip_log.txt
call %PY% -m pip install --upgrade pip > "%BUILD_LOGS%\pip_log.txt"

echo INSTALL REQUIREMENTS ^> %BUILD_LOGS%\req_log.txt
call %PY% -m pip install -r requirements.txt > "%BUILD_LOGS%\req_log.txt"
call %PY% -m pip install -r win_requirements.txt >> "%BUILD_LOGS%\req_log.txt"

echo UPDATE DB ^> %BUILD_LOGS%\upgrade_db_log.txt
call upgrade.bat > "%BUILD_LOGS%\upgrade_db_log.txt" 2>&1

echo BUILD ^> %BUILD_LOGS%\build_log.txt
call %PYI% %SPEC_FILE% --workpath %BUILD_LOGS% --distpath . > "%BUILD_LOGS%\build_log.txt" 2>&1

call build_aspose_convert.bat

echo CREATE ARCHIVE ^> %BUILD_LOGS%\create_archive_log.txt
call create_archive.bat > "%BUILD_LOGS%\create_archive_log.txt"