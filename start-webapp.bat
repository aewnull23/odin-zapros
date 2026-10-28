@echo off
cd /d "%~dp0webapp"
if not exist node_modules (
  call npm install
)
call npm run dev -- --host 127.0.0.1 --port 5173
pause
