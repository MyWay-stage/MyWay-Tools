@echo off
C:\TEMP\_runtime\python.exe -m pip install -r "%~dp0requirements_runtime.txt"
python -m PyInstaller Menu.spec --clean -y
xcopy /E /I /Y C:\TEMP\_runtime dist\MyWayTools\_runtime
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
echo DONE
pause