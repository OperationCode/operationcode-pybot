#!/bin/bash

ngrok_pid=$(pgrep ngrok)

check=$?

# check if the exit status returned success
if [ $check -eq 0 ]; then
    echo "Current ngrok PID = ${ngrok_pid}"
    echo "Killing current Ngrok instance..."
    kill -9 "$ngrok_pid"
    check=$?
    sleep 2
    if [ $check -eq 0 ]; then
        echo "Successfully killed previous Ngrok, starting new instance..."
        ngrok http 80 --log=stdout > ngrok.log &
        echo "Waiting for 5 seconds so Ngrok can start..."
        sleep 5

        # shellcheck disable=SC2155
        export NGROK_URL=$(curl http://localhost:4040/api/tunnels --silent | python -c "import json, sys; print(json.load(sys.stdin)['tunnels'][1]['public_url'])")
        echo "New Ngrok URL is: $NGROK_URL"

        echo "Please enter a name for your bot: "
        read -r bot_name
        export BOT_NAME=${bot_name}

        echo "Please enter in your first initial and last name - for example - 'jstevens'; this is what will be at the end of your slash commands in the Slack workspace: "
        read -r bot_username
        export BOT_USERNAME=${bot_username}
    else
        echo "Failed to kill previous Ngrok, ending execution..."
    fi
elif [ $check -eq 1 ]; then
    echo "No previous ngrok PID found, starting new instance..."
    ngrok http 80 --log=stdout > ngrok.log &
else
    echo "Problem locating and/or killing an existing Ngrok instance, ending execution..."
fi


