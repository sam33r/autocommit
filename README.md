# Ai-Commit-Gen

Ai-Commit-Gen is a Python binary that leverages various language models to generate meaningful commit messages. There's approximately a thousand such binaries out there, but none that fit into all of my workflows, so here's the 1001st.

ai-commit-gen can be called from scripts to automatically create commits, or integrated into editor workflows to create commit drafts.

## Installation

```bash
pip install ai-commit-gen
```

## Usage

ai-commit-gen assumes that the current working directory is, or is a subdirectory of, the git root.

- `-p` or `--prompt`: Override the default prompt for the language model. Available presets are "default", "refactoring", "documentation", and "mimic".

- `-c` or `--commit`: Not only generate a commit message but also commit the changes in git.

- `-m` or `--model`: Specify the model to be used. The default is "gpt-4o-mini". Supports a wide range of models from various providers through litellm.

- `-d` or `--debug`: Enable debug logging.

- `--apibase`: Specify a custom API base URL for the model provider.

## Supported Models

Ai-Commit-Gen uses litellm, which supports a wide range of language models from various providers. Some of the supported models include:

- OpenAI models (e.g., gpt-3.5-turbo, gpt-4)
- Anthropic models (e.g., claude-2)
- Local models via Ollama (e.g., ollama/llama3.1)

For a full list of supported models, please refer to the [litellm documentation](https://docs.litellm.ai/docs/providers).

## API Keys

For cloud-based models (like OpenAI or Anthropic), you'll need to provide an API key. The key can be set as an environment variable or stored in the system keyring:

- For OpenAI: Use `OPENAI_API_KEY` environment variable or store in keyring as "openai_key"
- For Anthropic: Use `ANTHROPIC_API_KEY` environment variable or store in keyring as "anthropic_key"

If the key is not found when the script is run, you will be prompted to enter it and given the option to store it in the keyring.

## Example

Here is an example of how you might use Ai-Commit-Gen:

```bash
# Stage your changes
git add .

# Just create the commit message
ai-commit-gen

# Generate a commit message and commit the changes
ai-commit-gen --commit

# Use a specific model
ai-commit-gen --model gpt-4

# Use a local model via Ollama
ai-commit-gen --model ollama/llama3.1

# Use a custom API base URL
ai-commit-gen --apibase "https://custom-api-endpoint.com/v1"
```
