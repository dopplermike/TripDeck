@echo off
cd /d "%~dp0"
py -m pip install pyshp shapely pyproj
if errorlevel 1 goto fail
py scripts\maps.py "%USERPROFILE%\Downloads"
if errorlevel 1 goto fail
echo Map ready. Commit and push using GitHub Desktop.
pause
exit /b 0
:fail
echo Map generation failed. Do not commit yet.
pause
exit /b 1
