#!/usr/bin/python3

import os
import sys
import time
import argparse
from litellm import completion, trim_messages
import keyring
import logging
import subprocess
import getpass


prompts = {
    "default": lambda: """As your response, please provide a concise git commit message for the changes described below.
The first paragraph of your response should be a single short line less than 50 characters. 
Add more paragraphs that describe the changes in more detail only if necessary. Prefer to use bullet lists instead of long paragraphs.""",
    "oneliner": lambda: "Please provide a one-liner git commit message for the changes described below. Your response will be used as the commit message.",
    "refactoring": lambda: "Please provide a detailed git commit message that explains the refactoring changes described below. Please detail every major change as a separate bullet point. Your response will be used as the commit message.",
    "documentation": lambda: "Please provide a git commit message that explains the documentation changes described below.",
    "mimic": lambda: f"Please provide a git commit message for the changes described below. Your message should closely mimic the style and structure of the following recent git commit messages in this repository: \n{get_last_commits()}",
}


def get_last_commits(num_commits=5):
    """
    Returns the commit messages of the last num_commits commits made in this git repository.
    """
    try:
        commit_messages = (
            subprocess.check_output(
                ["git", "log", "-n", str(num_commits), "--pretty=format:%B"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .split("\n\n")
        )  # decode and split the output into a list of commit messages

        # Prefix each commit message with "Example <N> - "
        commit_messages = [
            f"Example {i+1} - {msg}" for i, msg in enumerate(commit_messages)
        ]

        # Join the commit messages back together with double newlines
        commit_messages = "\n\n".join(commit_messages)

        return f"Recent commits:\n{commit_messages}\n\n"
    except subprocess.CalledProcessError:
        return ""


def get_provider(model):
    if model.startswith("gpt"):
        return "openai"
    elif model.startswith("claude"):
        return "anthropic"
    elif model.startswith("ollama/"):
        return "ollama"
    else:
        print(f"Invalid model: {model}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--prompt",
        default="default",
        help="""Specify the prompt for the OpenAI model. You can enter one of the following preset words:
        "default" - A general-purpose prompt requesting a git commit message for the described changes.
        "oneliner" - A prompt requesting a one-liner git commit message for the described changes.
        "refactoring" - A prompt requesting a git commit message specifically for refactoring changes.
        "documentation" - A prompt requesting a git commit message specifically for documentation changes.
        "mimic" - A prompt requesting a git commit message that mimics the style of recent commit messages.
        If you enter any other string, it will be used as the prompt directly. If no prompt is specified, the "default" prompt is used.""",
    )
    parser.add_argument(
        "-c", "--commit", action="store_true", help="Make the git commit directly"
    )
    parser.add_argument(
        "-m", "--model", default="gpt-3.5-turbo", help="Specify the model to be used (e.g., gpt-3.5-turbo, claude-2, ollama/llama2)"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    provider = get_provider(args.model)
    
    if provider != "ollama":
        # Get the API key from the environment variables or keyring.
        env_var = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        api_key = os.getenv(env_var)
        if api_key is None:
            api_key = keyring.get_password("ai_commit_gen", f"{provider}_key")
            if api_key is None:
                store_in_keyring = input(
                    f"No {provider.capitalize()} API key found. Would you like to store one in the keyring? (y/n) "
                )
                if store_in_keyring.lower() == "y":
                    api_key = getpass.getpass(f"Enter your {provider.capitalize()} API key: ")
                    keyring.set_password("ai_commit_gen", f"{provider}_key", api_key)
                else:
                    print(f"No {provider.capitalize()} API key provided. Exiting.")
                    sys.exit(1)
        # Remove any extra whitespace from the API key.
        os.environ[env_var] = api_key.strip()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]

    git_diff = os.popen("git diff --staged --no-color").read()

    # if git_diff empty or None, exit.
    if not git_diff:
        print("No changes to commit.")
        sys.exit(0)

    if args.prompt in prompts:
        prompt = prompts[args.prompt]()
    else:
        prompt = args.prompt or prompts["default"]()

    user_message = f"""{prompt}

Output of "git diff --staged": 
{git_diff}
"""

    messages.append({"role": "user", "content": user_message})

    # Trim messages to fit within model's context length
    messages = trim_messages(messages, args.model)

    # Note the start time.
    start_time = time.time()

    try:
        response = completion(
            model=args.model,
            messages=messages,
            api_base="http://localhost:11434" if provider == "ollama" else None
        )
    except Exception as e:
        logging.debug(f"Error calling LiteLLM API: {e}")
        sys.exit(1)

    end_time = time.time()

    # Log the time taken for the query.
    logging.debug(f"Query took {end_time - start_time:.2f} seconds")

    response_content = response.choices[0].message.content

    # If the commit flag was passed, make the commit.
    if args.commit:
        commit_message = [("-m " + p) for p in response_content.split("\n\n")]
        subprocess.run(["git", "commit"] + commit_message, check=True)
    else:
        print(response_content)


if __name__ == "__main__":
    main()
