<p align="center"><img width=20% src="https://github.com/asaezper/dagan/raw/develop/dagan/resources/logo.png"></p>

![Python](https://img.shields.io/badge/python-v3.5+-blue.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-GNU%20%20GPL%20v3.0-green.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

# dagan
Telegram Bot for UPV restaurants

## License
This project is licensed under the GNU GPLv3 - see the [LICENSE](LICENSE.) file for details

## Development utils
Prepare venv
```bash
python3 -m venv .venv --clear
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install -U setuptools wheel
.venv\Scripts\python.exe -m pip install -e .
```

Generate wheel
```bash
.venv\Scripts\python.exe setup.py bdist_wheel clean --all
```