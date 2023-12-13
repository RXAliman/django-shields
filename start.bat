@echo off
start cmd.exe /C "python manage.py runserver"
timeout /t 3
start chrome.exe --guest --start-maximized http://127.0.0.1:8000/masterlist