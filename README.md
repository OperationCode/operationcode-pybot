[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/operation_code.svg?style=social&label=Follow&style=social)](https://twitter.com/operation_code)
[![Code-style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


[![CircleCI](https://circleci.com/gh/OperationCode/operationcode-pybot.svg?style=svg)](https://circleci.com/gh/OperationCode/operationcode-pybot)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=OperationCode/operationcode-pybot)](https://dependabot.com)

# [OperationCode-Pybot](https://github.com/OperationCode/operationcode-pybot)

OperationCode PyBot is a Python [Slack Bot](https://api.slack.com)
extending [Pyslacker's](https://pyslackers.com/)
[sir-bot-a-lot](https://github.com/pyslackers/sir-bot-a-lot-2)
framework.

## Resources
* [Slack Bot Tutorial](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html)
* [Slack Events API Framework](https://github.com/slackapi/python-slack-events-api)
* [sir-bot-a-lot](https://github.com/pyslackers/sir-bot-a-lot-2)


## Contributing
Bug reports and pull requests are welcome on [Github](https://github.com/OperationCode/operationcode-pybot). This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct. If you wish to assist, join the [\#oc-python-projects](https://operation-code.slack.com/messages/C7NJLCCMB/) rewrite to learn how to contribute.

## Quick Start
Recommended versions of tools used within the repo:
- `python@3.7` or greater (in some environments, you may need to specify version of python i.e. `python test.py` vs `python3 test.py`))
- `git@2.17.1` or greater
- `poetry@0.12.11` or greater
    - [Poetry](https://poetry.eustace.io/) is a packaging and dependency manager, similar to pip or pipenv
    - Poetry provides a custom installer that can be ran via `curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python`
    - Alternatively, poetry can be installed via pip/pip3 with `pip install --user poetry` or `pip3 install --user poetry`
    - See https://poetry.eustace.io/docs/


```bash
# Install dependencies (ensure poetry is already installed)
poetry install

# Run local development
poetry run python -m pybot

# Run testing suite
poetry run pytest

# Run formatting and linting
poetry run black .
# the next line shouldn't output anything to the terminal if it passes
poetry run flake8
poetry run isort -rc .
```


## License
This package is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
