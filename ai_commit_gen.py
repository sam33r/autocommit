#!/usr/bin/python3

import os
import sys
import time
import argparse
from litellm import completion
from litellm.utils import trim_messages
import keyring
import logging
import subprocess
import getpass


prompts = {
    "default": lambda: """
You are an expert software engineer.
Review the provided diffs which are about to be committed to a git repo.
Review the diffs carefully.
Generate a commit message for those changes.
The commit message MUST use the imperative tense.
Reply with JUST the commit message, without quotes, comments, questions, etc!
""",
    "refactoring": lambda: """
Please provide a detailed git commit message that explains the refactoring changes described below.
Please detail every major change as a separate bullet point.
Reply with JUST the commit message, without quotes, comments, questions, etc!
""",
    "documentation": lambda: """
Please provide a git commit message that explains the documentation changes described below.
Reply with JUST the commit message, without quotes, comments, questions, etc!
""",
    "mimic": lambda: f"""
Please provide a git commit message for the diffs provided below.
Your message should closely mimic the style and structure of the following recent git commit messages in this repository:

{get_last_commits()}

Reply with JUST the commit message, without quotes, comments, questions, etc!
""",
}


def get_last_commits(num_commits=5):
    """
    Returns the commit messages of the last num_commits commits.
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
    """
    Returns the provider of the model.
    """
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
        help="""Specify the prompt for the llm model. You can enter one of the following preset words:
        "default" - A general-purpose prompt requesting a git commit message for the described changes.
        "refactoring" - A prompt requesting a git commit message specifically for refactoring changes.
        "documentation" - A prompt requesting a git commit message specifically for documentation changes.
        "mimic" - A prompt requesting a git commit message that mimics the style of recent commit messages.
        If you enter any other string, it will be used as the prompt directly. If no prompt is specified, the "default" prompt is used.""",
    )
    parser.add_argument(
        "-c", "--commit", action="store_true", help="Make the git commit directly"
    )
    parser.add_argument(
        "-m", "--model", default="gpt-4o-mini", help="Specify the model to be used (e.g., gpt-3.5-turbo, claude-2, ollama/llama2)"
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
