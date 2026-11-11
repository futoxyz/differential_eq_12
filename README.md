# ДУ № 1 вариант 12

Запуск через uv
```shell
uv venv
.venv/Scripts/activate # или source .venv/Scripts/activate
uv sync

py -m src.main
```

Запуск через python
```shell
python -m venv .venv
.venv/Scripts/activate # или source .venv/Scripts/activate
pip install -r requirements.txt

py -m src.main
```

Структура
```text
src/
├──__init__.py
├──main.py            # Запуск программы с заданными входными данными
├──model.py           # Реализация построения и вычисления моделей
├──constants.py       # Используемые константы. Можно заменять
report/
├──report.pdf         # Описание решения, отчет
├──report.tex         # Исходный отчет в latex
.gitignore
.python-version
pyproject.toml        # Зависимости
README.md
requirements.txt      # Зависимости
uv.lock
```