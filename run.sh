#!/bin/bash
echo "Запуск PinParse..."
VENV_DIR="venv"
PYTHON="python3"

# Проверка наличия виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    $PYTHON -m venv $VENV_DIR
fi

# Активация виртуального окружения
source $VENV_DIR/bin/activate

# Установка зависимостей
echo "Установка необходимых библиотек..."
pip install -r requirements.txt

# Запуск приложения
echo "Запуск приложения..."
python3 main.py

# Деактивация виртуального окружения
deactivate