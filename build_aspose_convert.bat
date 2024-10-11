@echo off
set "VENV_NAME=.venv"
set "BUILD_LOGS=.build_logs"
set "SCRIPTS=.\%VENV_NAME%\Scripts"
set "PY=%SCRIPTS%\python.exe"
set "PYI=%SCRIPTS%\pyinstaller.exe"
set "SPEC_FILE=build_aspose_convert.spec"

echo ASPOSE BUILD ^> %BUILD_LOGS%\aspose_build_logs.txt
call %PYI% %SPEC_FILE% --workpath %BUILD_LOGS% --distpath . > "%BUILD_LOGS%\aspose_build_logs.txt" 2>&1