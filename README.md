![Pieces CLI for Developers](https://camo.githubusercontent.com/69c990240f877927146712d45be2f690085b9e45b4420736aa373917f8e0b2c8/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f7069656365735f7374617469635f7265736f75726365732f7066645f77696b692f5049454345535f4d41494e5f4c4f474f5f57494b492e706e67)
<p align="center">

# <p align="center"> Pieces Python CLI Tool

<p align="center"> This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with Pieces OS. It provides a range of functionalities such as asset management, application interaction, and integration with various Pieces OS features.

</p>
  
##### <p align="center"> [Website](https://pieces.app/) • [Pieces OS Documentation](https://docs.pieces.app/) • [Pieces Python CLI Documentation](https://github.com/pieces-app/cli-agent/blob/prod/Documentation.md)
</p>
<br>

### Table of Contents
- [Operating System Support](#operating-system-support)
- [Installing](#installing)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Run](#run)
  - [List Assets](#list-assets)
  - [Open, Save, Create, Edit, and Delete Assets](#open-save-create-edit-delete-assets)
  - [Search and Query](#search-and-query)
  - [Additional Commands](#additional-commands)
- [Supported Versions](#supported-versions)

#### Operating System Support
The Pieces Python CLI Tool is compatible with various operating systems, ensuring a wide range of usage and adaptability. While it offers full support across most systems, specific features might have varied performance based on the OS environment.

The CLI Supports
- Windows 10 or greater
- Mac
- Windows

#### Installing
To get started with the Pieces Python CLI Tool, you need to:

1. Ensure Pieces OS is installed and running on your system.
2. Install the Python package:

   ```bash
   pip install pieces-cli
   ```

   ```bash
   brew install pieces-cli
   ```

   ```bash
   conda install pieces-cli
   ```

#### Getting Started
After installing the CLI tool, you can access its functionalities through the terminal. The tool is initialized with the command `pieces` followed by various subcommands and options.

### Usage

#### Run
The run command starts the CLI in a loop. While you can use each command without running the CLI in a loop you'll get much faster results and a better experience using run. 

Once the CLI is running in a loop you can simply type the command.

    For instance: 
    open

    Instead of: 
    pieces open

If you have a numbered list or search open you can just type the number and it will open the asset associated. 

```bash
  pieces run
  ```

#### List Assets
To list assets or applications, use the command:

##### Default of 10
  ```bash
  pieces list
  ```

##### Lists your x most recent assets
  ```bash
  pieces list x
  ```

##### Lists all registered applications
  ```bash
  pieces list apps
  ```

##### Lists all accessible AI models 
  ```bash
  pieces list models
  ```

##### Open, Save, Create, Edit, and Delete Assets

##### Open an asset:

Opens an asset from a list or search. If only "open" is used then it will open your most recent asset. This also creates a link to the asset's code.

```bash
pieces open [ITEM_INDEX]
```

##### Save the current asset:

** Does Not Currently Work **

```bash
pieces save
```

##### Create a new asset:

Will take whatever text is copied to your clipboard and create an asset. The asset will automatically be scanned and recognized for it's file type. 

```bash
pieces create
```

##### Edit an existing asset:

This currently only works for an assets's name

```bash
pieces edit
```

##### Delete an asset:

This will delete an opened asset by using list or search first. If you do not have an opened asset it will open your most recent asset and ask if you'd like to delete it. 

```bash
pieces delete
```

#### Search and Query
##### Perform a fuzzy search:

```bash
pieces search [your query]
```

Finds strings that approximately match patterns. Normal search.

##### Perform a Neural Code Search:
```bash
pieces search query --mode ncs
```

Uses machine learning, deep neural networks, and natural language processing. It can understand the intent of a user's search query and match it with the most relevant results.

##### Perform a Full Text Search:
```bash
pieces search query --mode fts
```

Examines all words in a document to find matches to search criteria.

##### change the llm model you are using:

Change the model in the ask command.

```bash
pieces change_model [MODEL_INDEX]
```
##### Ask a question to a model:
** Requires quotes around question **

Ask the copoilt a question it uses chatGPT3 as a defualt model to ask a question, you can change the model using the change model command.

```bash
pieces ask "your question"
```


##### Commiting to github

Auto commit the code to github and generate a commit message you can use the `-p` or `--push` flags to push the code to the repo too

```bash
pieces commit -p
```

#### Additional Commands
##### Retrieve the version of Pieces OS and the CLI:

```bash
pieces version
```

##### For a detailed help menu:

```bash
pieces help
```

##### Supported Versions
- Windows 10 or Greater
- Mac (insert later)
- Linux (insert later)

It is advised to keep the CLI tool updated to the latest version to ensure compatibility with Pieces OS and access to all features. Please refer to our documentation for details on supported versions.

## Contributing

To run this project locally, follow these steps:

1. Fork this project via GitHub. 

2. Clone this project: 
```shell
git clone https://github.com/pieces-app/cli-agent
```

3. Create a Virtual Environment
```shell
python3 -m venv venv
``` 

4. Activate Your Virtualenv
```shell
source venv/bin/activate for Mac & Linux OS

cd venv\Scripts for Windows OS
activate 
```

5. This project uses poetry for managing dependencies and builds. Install poetry with:
```shell
pip install poetry
```

6. Then use poetry to install the required dependencies
```shell
poetry install
```

7. You build with
```shell
poetry build
```

8. Finally any project dependencies should be added to the pyproject.toml file with
```shell
poetry add 
```

9. Open the Dist folder
```shell
cd dist
``` 

10. Install the WHL file
```shell
pip install pieces-0.0.14-py3-none-any.whl
``` 

11. To view all the CLI Commands
```shell 
Pieces help 
``` 

these can be local/github/pypi etc.