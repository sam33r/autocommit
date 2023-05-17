#!/usr/bin/python3

import os
import sys
import time
import argparse
import openai
import keyring
import logging
import subprocess
import getpass

def get_root_dir_name():
    """
    Returns the name of the root git directory.
    """
    try:
        root_dir = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        return f"Repository root dir: {os.path.basename(root_dir.strip())}\n\n"
    except subprocess.CalledProcessError:
        return ""

def get_last_commits(num_commits=3):
    """
    Returns the commit messages of the last num_commits commits made in this git repository.
    """
    try:
        commit_messages = subprocess.check_output(["git", "log", "-n", str(num_commits), "--pretty=format:%B"])
        return f"Recent commits:\n{commit_messages.decode()}\n\n"
    except subprocess.CalledProcessError:
        return ""

def get_character_limit(model):
    # Determine character limit based on the model.
    if model == "gpt-3.5-turbo":
        return 12000
    elif model == "gpt-4":
        return 25000
    elif model == "gpt-4-32k":
        return 120000
    else:
        print(f"Invalid model: {model}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--prompt", help="Specify the prompt for the OpenAI model"
    )
    parser.add_argument(
        "-c", "--commit", action="store_true", help="Make the git commit directly"
    )
    parser.add_argument(
        "-m", "--model", default="gpt-3.5-turbo", help="Specify the model to be used"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Get the OpenAI API key from the environment variables or keyring.
    api_key = os.getenv("OPENAI_KEY")
    if api_key is None:
        api_key = keyring.get_password("autocommit", "openai_key")
        if api_key is None:
            store_in_keyring = input(
                "No OpenAI API key found. Would you like to store one in the keyring? (y/n) "
            )
            if store_in_keyring.lower() == 'y':
                api_key = getpass.getpass("Enter your OpenAI API key: ")
                keyring.set_password("autocommit", "openai_key", api_key)
            else:
                print("No OpenAI API key provided. Exiting.")
                sys.exit(1)
    openai.api_key = api_key

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]

    git_diff = os.popen("git diff --staged --no-color").read()
    char_limit = get_character_limit(args.model)

    # if git_diff empty or None, exit.
    if not git_diff:
        print("No changes to commit.")
        sys.exit(0)

    if len(git_diff) > char_limit:
        git_diff = git_diff[:char_limit] + f" (cut off at {char_limit} characters)."

    # Create prompt.
    prompt = (
        args.prompt
        if args.prompt
        else (
        f"""As your response, please provide a concise git commit message for the changes described below.

The first paragraph of your response should be a single short line to serve as the title of the commit. 

Add more paragraphs that describe the changes in more detail only if necessary. Prefer to use bullet lists instead of long paragraphs.

{get_root_dir_name()}{get_last_commits()}

Output of "git diff --staged": 
{git_diff}
"""
        )
    )

    messages.append({"role": "user", "content": prompt})

    # Note the start time.
    start_time = time.time()

    try:
        response = openai.ChatCompletion.create(model=args.model, messages=messages)
    except Exception as e:
        logging.debug(f"Error calling OpenAI API: {e}")
        sys.exit(1)

    end_time = time.time()

    # Log the time taken for the query.
    logging.debug(f"Query took {end_time - start_time:.2f} seconds")

    response_content = response["choices"][0]["message"]["content"]

    # If the commit flag was passed, make the commit.
    if args.commit:
        commit_message = [("-m " + p) for p in response_content.split("\n\n")]
        subprocess.run(['git', 'commit'] + commit_message, check=True)
    else:
        print(response_content)


if __name__ == "__main__":
    main()
