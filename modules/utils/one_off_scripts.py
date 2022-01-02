import sys
import os
import re
import json
from dotenv import load_dotenv
from modules.airtable import daily_programmer_table


load_dotenv()


def main(script_to_run: str) -> None:
    if script_to_run == "process_daily_programmer_files":
        process_daily_programmer_files(sys.argv[2])


def process_daily_programmer_files(files_directory: str) -> None:
    for filename in os.listdir(files_directory):
        with open(files_directory + "/" + filename, "r") as file:
            message_list = json.load(file)
            for message in message_list:
                if message["text"]:
                    print(f"Parsing a new message in file: {filename}")
                    title = re.search(r"(={2,3}.*={2,3})", message["text"])
                    if title:
                        name = re.search(r"(\[.*?])", message["text"])
                        if name:
                            try:
                                daily_programmer_table.create_record(
                                    {
                                        "Name": name[0]
                                        .replace("[", "")
                                        .replace("]", "")
                                        .replace("*", ""),
                                        "Text": message["text"][name.span()[1] + 1 :],
                                        "Initially Posted On": filename.split(".")[0],
                                        "Last Posted On": filename.split(".")[0],
                                        "Posted Count": 1,
                                        "Initial Slack TS": message["ts"],
                                        "Blocks": message["blocks"],
                                    }
                                )
                            except KeyError:
                                daily_programmer_table.create_record(
                                    {
                                        "Name": name[0]
                                        .replace("[", "")
                                        .replace("]", ""),
                                        "Text": message["text"][name.span()[1] + 1 :],
                                        "Initially Posted On": filename.split(".")[0],
                                        "Last Posted On": filename.split(".")[0],
                                        "Posted Count": 1,
                                        "Initial Slack TS": message["ts"],
                                    }
                                )


if __name__ == "__main__":
    main(sys.argv[1])
