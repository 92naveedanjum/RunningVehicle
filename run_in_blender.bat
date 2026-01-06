@echo off
REM This batch file runs your Python script in Blender
REM Replace the path below with your actual Blender installation path

set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
set SCRIPT_PATH="%~dp0Garden (1).py"

echo Running script in Blender...
%BLENDER_PATH% --python %SCRIPT_PATH%

pause
