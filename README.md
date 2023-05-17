# Ai-Commit-Gen

Ai-Commit-Gen is a Python binary that leverages OpenAI's language models to generate meaningful commit messages. There's approximately a thousand such binaries out there, but none that fit into all of my workflows, so here's the 1001st.

ai-commit-gen can be called from scripts to automatically create commits, or integrated into editor workflows to create commit drafts.

## Installation

```bash
pip install ai-commit-gen
```

## Usage

ai-commit-gen assumes that the current working directory is, or is a subdirectory of, the git root.

- `-p` or `--prompt`: Override the default prompt for the OpenAI model.

- `-c` or `--commit`: Not only generate a commit message but also commit the changes in git.

- `-m` or `--model`: Specify the model to be used. The default is "gpt-3.5-turbo". The models "gpt-4" and "gpt-4-32k" are also supported.

- `-d` or `--debug`: Enable debug logging.

## OpenAI API Key

The OpenAI API key can either be set as an environment variable `OPENAI_KEY`, or it can be stored in the system keyring, which is how I use it. 

If the key is not found in either of these locations when the script is run, you will be prompted to enter the key and given the option to store it in the keyring.

## Example

Here is an example of how you might use Ai-Commit-Gen:

```bash
# Stage your changes
git add .

# Just create the commit message
ai-commit-gen

# Generate a commit message and commit the changes
ai-commit-gen --commit
```

In the above example, Ai-Commit-Gen will consider the staged changes, generate a commit message using the OpenAI model, and directly commit the changes with the generated message.

## Note

Please make sure that you have the required permissions and credits to use the OpenAI API. 

## Contribute

Feel free to open an issue or submit a pull request if you have any issues or feature requests.
