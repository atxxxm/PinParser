@echo off
echo Запуск PinParse...
set "VENV_DIR=venv"
set "PYTHON=python"

:: Проверка наличия виртуального окружения
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Создание виртуального окружения...
    %PYTHON% -m venv %VENV_DIR%
)

:: Активация виртуального окружения
call %VENV_DIR%\Scripts\activate.bat

:: Установка зависимостей
echo Установка необходимых библиотек...
pip install -r requirements.txt

:: Запуск приложения
echo Запуск приложения...
python main.py

:: Деактивация виртуального окружения
deactivate
pause