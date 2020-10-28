<div align="center">
  <a href="https://operationcode.org" height="750" width="750">
    <img
      alt="Operation Code Hacktoberfest Banner"
      src="https://operation-code-assets.s3.us-east-2.amazonaws.com/operationcode_hacktoberfest_2020.jpg"
    >
  </a>
</div>
<br />
<br />

# 🎃 Hacktoberfest 🎃	

[All the details you need](https://github.com/OperationCode/START_HERE/blob/master/README.md#-hacktoberfest-) before participating with us during Hacktoberfest.	

<br />

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/operation_code.svg?style=social&label=Follow&style=social)](https://twitter.com/operation_code)
[![Code-style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


[![CircleCI](https://circleci.com/gh/OperationCode/operationcode-pybot.svg?style=svg)](https://circleci.com/gh/OperationCode/operationcode-pybot)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=OperationCode/operationcode-pybot)](https://dependabot.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://contributor-covenant.org/)

# [OperationCode-Pybot](https://github.com/OperationCode/operationcode-pybot)

OperationCode PyBot is a Python [Slack Bot](https://api.slack.com)
extending [Pyslacker's](https://pyslackers.com/)
[sir-bot-a-lot](https://github.com/pyslackers/sir-bot-a-lot-2)
framework.

## Resources
* [Slack Bot Tutorial](https://www.digitalocean.com/community/tutorials/how-to-build-a-slackbot-in-python-on-ubuntu-20-04)
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

In order to do this, you'll want to tackle the following items in order:

1. Setup your own Slack workspace.
2. Grab a signing secret from Slack that pybot can utilize.
3. Launch pybot locally, passing it your Slack signing secret.
4. Attach your pybot instance to the public internet so that Slack can speak
   with it.
5. Point Slack at your running pybot instance, and properly configure it.

The following sections will guide you through each of these stages.

### 1 - Setup Your Own Slack Workspace

To start, you'll want to visit Slack's [Getting
Started](https://slack.com/get-started) page. From this page, follow the steps
required to create a new workspace. The names/options you configure during
creation don't matter so much, but make sure you associate it with an email
address you have access to. Once complete it should present you with an option
to login to the new workspace, make sure you go ahead and do that.

If you're having a hard time figuring this out, try checking out the following
Slack article [Create a Slack Workspace](https://slack.com/intl/en-ca/help/articles/206845317-Create-a-Slack-workspace).

#### Create expected channels
Several of Pybot's features involve sending messages to specific channels - in order
for this to work in your personal Slack workspace you'll need to create the following channels:
- mentors-internal
- greetings
- moderators
- oc-tech


### 2 - Create a pybot App in Your Slack Workspace

The next step is to create a new bot application in your workspace. While still
logged in, visit the [App Management](https://api.slack.com/apps) page and
choose to create a new app. During this process, make sure to copy down the
signing secret key that gets generated for your app, as you'll need it later,
following this, follow the guidelines for creating a bot app as laid out in the
[Enabling interactions with bots](https://api.slack.com/bot-users) article. When
you get to the stage of creating the bot user, make sure to write down the bot
user OAuth access token that is presented, as you'll need to use it later.

On the `OAuth & Permissions` page configure the Pybot app with the following scopes

- channels:manage
- chat:write
- chat:write.public
- commands
- users:read

### 3 - Launch pybot Locally, Passing in Your Signing Secret

With your Slack workspace, app and bot user created, and your app signing secret
and bot user OAuth access token in hand, you should now be ready to configure
pybot to integrate with your new Slack workspace. To do this, you'll first want
to setup the proper configuration in pybot.

pybot configuration is specified completely through environment variables. When
running locally, you can configure the _./docker/pybot.env_ file with the
environment variable name/value pairings, which will get evaluated on
application start. Otherwise, make sure to export or pass in the correct
environment variables through your shell when launching pybot.

Here's an example of configuring these through the _pybot.env_ file:

```bash
SLACK_BOT_SIGNING_SECRET=APP-SIGNING-SECRET
BOT_USER_OAUTH_ACCESS_TOKEN=BOT-USER-OAUTH-TOKEN
```

**NOTE**: More configuration settings than these may be specified. Please see
the _Known Configuration Settings_ section near the bottom of this document
for details on other settings that can be set.

### 4 - Attach Your pybot Instance to the Public Internet

With an instance of pybot running, you now need to expose this instance to the
public internet so Slack can send in API requests. You can easily utilize ngrok
for this purpose if you wish. To do so; download ngrok from https://ngrok.com/download
and set up a tunnel like so:

```bash
ngrok http 5000
```

Pay attention to copy out the response you get and keep this command running.
Here's an example output from the command:

```bash
ngrok by @inconshreveable                                                                        (Ctrl+C to quit)
Session Status                online                                                                             
Session Expires               7 hours, 56 minutes                                                                
Version                       2.3.35                                                                             
Region                        United States (us)                                                                 
Web Interface                 http://127.0.0.1:4040                                                              
Forwarding                    http://9d73595a7aac.ngrok.io -> http://localhost:5000                              
Forwarding                    https://9d73595a7aac.ngrok.io -> http://localhost:5000                             
Connections                   ttl     opn     rt1     rt5     p50     p90                                        
                              0       1       0.00    0.00    0.00    0.00                                       
HTTP Requests 
```

With this done, ngrok will now expose the instance of pybot running locally
on port 5000 via the "Forwarding" address it returns.  Be sure to use the URL
beginning with http**s**.

### 5 - Point Slack at Your Running pybot Instance

With the initial Slack configuration complete and your instance of pybot
running on the public internet, it is now the perfect time to fully configure
Slack to interact with your bot. Depending on the interactions you're wanting to
play with, there are various configurations you can specify, which can be
broken down into the following parts:

*  Event Subscriptions - this allows pybot to respond to various events that may
   occur in your Slack workspace.
*  Slash Commands - this allows a user to invoke various commands from any
   channel in your workspace to interact with pybot.
*  Interactive Components - this allows various options to be exposed when
   right clicking on a message, or, when the bot presents various user
   elements that can be interacted with, instructs Slack on where to send the
   results for such interactions.

High level steps for configuring each of these can be found in the following
sub-sections; note that you don't need to necessarily configure all of these,
it all depends on what areas of pybot you're wanting to play with.

#### Event Subscriptions

You can follow the instructions (and read helpful related information) on the
[Events API](https://api.slack.com/events-api) page on Slack to setup event
subscriptions. When configuring your events URI; make sure you pass in the
Base-URI that pybot is listening on followed by the text _/slack/events_. For
example:

    https://123_random_code_321.ngrok.io/slack/events

Additional setup may needed depending on the type of events pybot is subscribing to. 
For example, in order to work on the app's functionality on a `team_join` event, you need to:  

* Add `team_join` to workspace event
* Make sure `greetings` channel exists and ensure the app is invited to the channel
* Add necessary OAuth scopes to the app e.g. `users:read`, `chat:write`, etc.

#### Slash Commands

You can follow the instructions (and read helpful relation information) on the
[Enabling interactivity with Slash Commands](https://api.slack.com/interactivity/slash-commands)
page on Slack to setup pybot slash commands. When configuring a Slash command,
make sure you configure the request URL to match the Base-URI that pybot is
listening on followed by the text _/slack/commands_. For example:

    https://123_random_code_321.ngrok.io/slack/commands
   
You'll use the same URI for each command. Here's a table listing of currently
supported commands along with some suggested configuration text:

Command | Description | Usage Hint
------- | ----------- | ----------
/lunch | find lunch suggestions nearby | &lt;zip code> &lt;distance in miles>
/mentor | request mentoring |
/mentor-volunteer | offer to mentor others |
/repeat | parrot canned messages | &lt;10000|ask|ldap|merge|firstpr|channels|resources>
/report | report something to the admins | <text of message>
/roll | roll x dice with y sides | <XdY>
/ticket | submit ticket to admins | (text of ticket)


**👋 IMPORTANT!**

The `/lunch` command requires a valid Yelp API token stored in the `YELP_TOKEN` 
environment variable. See https://www.yelp.com/developers/faq

Similarly, the `/mentor` and `/mentor-volunteer` commands require access to an Airtable
environment with a specific configuration.  If you're planning on working with the mentor
functionality please reach out to the `#oc-python-projects` channel for help getting set up.  

#### Interactive Components

You can follow the instructions (and read helpful related information) on the
[Handling user interaction in your Slack apps](https://api.slack.com/interactivity/handling)
page on Slack to setup Slack interactive component configuration. When
configuring the request URL, you'll want to set it to the Base-URI that pybot
is listening on followed by the text _/slack/actions_. For example:

    https://123_random_code_321.ngrok.io/slack/actions

You'll also want to make sure to configure the report message action with the
following parameters:

Name | Description | Callback ID
---- | ----------- | -----------
Report Message | Report this message to admins | report_message

## Known Configuration Settings

This application has a number of environment variables that can be set when
launching to alter the behaviour of the application. The list below is an
incomplete description of a number of them. Please feel free to update this
list with more details via a PR:

Name | Description | Example
---- | ----------- | -------
SLACK_BOT_SIGNING_SECRET | The unique signing secret used by Slack for a specific app that will be validated by pybot when inspecting an inbound API request | f3b4d774b79e0fb55af624c3f376d5b4
BOT_USER_OAUTH_ACCESS_TOKEN | The bot user specific OAuth token used to authenticate the bot when making API requests to Slack | xoxb-800506043194-810119867738-vRvgSc3rslDUgQakFbMy3wAt

## License
This package is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
