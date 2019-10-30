<div align="center">
  <br />
  <a href="https://operationcode.org">
    <img
      alt="Operation Code Hacktoberfest Banner"
      src="https://operation-code-assets.s3.us-east-2.amazonaws.com/operation_code_hacktoberfest_2019.jpg"
    >
  </a>
  <br />
  <br />
</div>

# 🎃 Hacktoberfest 🎃

[All the details you need](https://github.com/OperationCode/START_HERE/blob/master/README.md#-hacktoberfest-) before participating with us.

<br />

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

## How to Test Integration With Slack

After having developed some new feature, or having in hand what you believe is
a fix for an existing bug, how do you test it out in a real system in order to
make sure that your changes do all that you hope they do? The answer; bring up
the application in your own environment and hook it up to Slack!

In order to do this, there are 6 main things you need to accomplish:

1. Setup your own Slack workspace.
2. Grab a signing secret from Slack that pybot can utilize.
3. Launch pybot locally, passing it your Slack signing secret.
4. Attach your pybot instance to the public internet so that Slack can speak
   with it.
5. Point Slack at your running pybot instance, and properly configure it.
6. Relish in your success!

The following sections will guide you through each of these stages.

### 1 - Setup Your Own Slack Workspace

To start, you'll want to visit Slack's [Getting
Started](https://slack.com/get-started) page. From this page, choose the option
to create a new workspace. It will request that you enter in an email address,
feel free to enter in an email address that you have access to and continue
through the process. It will email you a 6 digit code, check your email for
this code and then input it into Slack to continue the process. Enter in the
name of the workspace that you're going to play around with the pybot in. When
it asks for a project you're working on, put in whatever you want. Maybe pybot
would be a good choice? It will ask you to input other team members that you'd
like to join in. Feel free to put in other emails here, or just skip this step
altogether. Then, it gives you an option to login to your new workspace. Go
ahead and do that!

With your new workspace created, you'll see that it has created a channel for
the project name you entered. Congratulations, you've completed the first stage!

### 2 - Create a pybot App in Your Slack Workspace

While logged in to your Slack workspace, click on the drop-down menu in the top
left corner, find the administration menu and then select _Manage Apps_. Once
here, to the top right, find the build option and select it. It will bring you
to the Slack API page. Click on the _Start Building_ option. From here, it will
prompt you to enter in an application name and to attach it to a workspace. Go
ahead and name your new pybot bot and attach it to your newly created workspace.
Then click _Create App_ to do the deed. It will bring you to a new page. On this
page, find the app credentials section, and from here, copy out your app's new
signing secret. This is what you'll configure pybot with so that it can
authenticate inbound requests.

Next, near the top of the screen select Add features and functionality and
then chose _Bots_. Click on the _Add a Bot User_ button, add in a display name,
enable _Always Show My Bot as Online_ and then select _Add Bot User_. Then, to
the left, under Settings, choose _Install App_ and then click on _Install App to
Workspace_, click _Allow- and then copy off the bot user OAuth access token for
later. You'll also be configuring pybot with this so that it can authenticate
itself with Slack.

### 3 - Launch pybot Locally, Passing in Your Signing Secret

Either configure a pybot.env file in the root of this repository, or set an
exported variable in your shell environment. Here's the required parameters
shown as being configured in pybot.env (these also can be set as environment
variables in your shell of choice instead.)

Example _pybot.env_:

```text
SLACK_BOT_SIGNING_SECRET=SUPER-SECRET-SIGNING-SECRET-HERE
BOT_OAUTH_TOKEN=BOT-USER-OAUTH-ACCESS-TOKEN-HERE
SLACK_BOT_USER_ID=BOT-DISPLAY-NAME
```

### 4 - Attach Your pybot Instance to the Public Internet

You can easily utilize serveo to publish your pybot instance to the public
internet. Just run the following command from your UNIX like workstation to
setup an SSH port tunnel to serveo:

```bash
ssh -R 80:localhost:5000 serveo.net
```

Pay attention to copy out the response you get and keep this command running.
Here's an example output from the command:

```text
Forwarding HTTP traffic from https://supersecret.serveo.net
Press g to start a GUI session and ctrl-c to quit.
```

### 5 - Point Slack at Your Running pybot Instance

From the Slack API interface that you used to create your bot, under Features
on the left, select _Event Subscriptions_, slide it to on, paste in your serveo
Base-URI followed by _/pybot/api/v1/slack/verify_ (IE:
_https://cool.serveo.net/pybot/api/v1/slack/verify_) and then save your changes.

Everything should now be done!

## License
This package is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
