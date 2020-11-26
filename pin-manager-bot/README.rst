Daily Programmer Bot
====================

This repository contains the source code for a bot for `@OperationCode <https://github.com/OperationCode>`_.

This bot will extract slack messages containing a problem and push them to a github gh-pages repository.

Check `Issue #189 <https://github.com/OperationCode/operationcode-pybot/issues/189>`_


Usage
-----

1) Make sure you have python >= 3.6 and ngrok

2) Create a virtual env and activate it

    .. code-block:: bash
        
        python -m virtualenv env
        source env/bin/activate

3) Install dependencies

    .. code-block:: bash
        
        pip install -r pin-manager-bot/requirements.txt

4) Create a `config.ini` file containing the link to the github repo where you want the challenges to be pushed like this

    .. code-block:: ini

        [GitRepoInfo]
        repo = git@github.com:73VW/Daily-Programmer-Bot.git

5) Export bot env variables (check `this link <https://api.slack.com/start/building/bolt-python#credentials>`_)

6) Install the app. See `this page <https://api.slack.com/start/building/bolt-python#install>`_

7) Run the bot from `__main__.py file`. The bot will now list challenges already in the channel `daily-programmer`.

8) Run ngrok https://api.slack.com/start/building/bolt-python#ngrok.

9) Change Request URl `here <https://api.slack.com/apps/A01CG55DG8N/event-subscriptions?>`_

The bot now listens to the channel. When a new challenge is sent, the bot adds it to the list.