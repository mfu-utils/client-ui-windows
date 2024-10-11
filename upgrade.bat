@echo off
set "ALEMBIC=.venv\Scripts\alembic.exe"
call %ALEMBIC% upgrade head
call console.bat seed