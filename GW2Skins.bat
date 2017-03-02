@echo off
python GUI.py 

if %ERRORLEVEL%=="0"  (
	echo fine
	exit 0
)
if %ERRORLEVEL%==9009" ( 
	echo Python not installed. Please install python 2.3.17
	pause
)
if %ERRORLEVEL%==1 ( 
	echo If above is "ImportError" please install PIL (http://www.pythonware.com/products/pil/ or http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe) and execute "pip install requests"
	pause
) 

echo Something wrong happened... Report a bug
pause