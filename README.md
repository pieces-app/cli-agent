![Pieces CLI for Developers](https://camo.githubusercontent.com/69c990240f877927146712d45be2f690085b9e45b4420736aa373917f8e0b2c8/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f7069656365735f7374617469635f7265736f75726365732f7066645f77696b692f5049454345535f4d41494e5f4c4f474f5f57494b492e706e67)
<p align="center">

# <p align="center"> Pieces Python CLI Tool

<p align="center"> This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with Pieces OS. It provides a range of functionalities such as asset management, application interaction, and integration with various Pieces OS features.

</p>
  
##### <p align="center"> [Website](https://pieces.app/) • [Pieces OS Documentation](https://docs.pieces.app/) • [Pieces Python CLI Documentation](https://github.com/pieces-app/cli-agent/blob/prod/Documentation.md)
</p>

# Important

Make sure you have [**Pieces OS**](https://docs.pieces.app/installation-getting-started/what-am-i-installing) installed in order to run the Pieces CLI tool.

### Table of Contents
- [Operating System Support](#operating-system-support)
- [Installing](#installing)
- [Getting Started](#getting-started)
- [Terminologies](#some-important-terminologies)
- [Usage](#usage)
  - [Run](#run)
  - [List (assets,apps,models)](#list-command)
  - [Open, Save, Create, Edit, and Delete Assets](#open)
  - [Search and Query](#search-and-query)
  - [Change the model](#change-the-llm-model-you-are-using)
  - [conversations/conversation](#conversations-command)
  - [Change Model](#change-model)
  - [Ask a Question](#ask-a-question-to-a-model)
  - [login and logout](#login-and-logout)
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


### Some important terminologies

- `x` -> The index
- `current asset` -> The asset that you are currently using can be changed by the open command 
- `current conversation` -> The conversation that you currently using in the ask command


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

#### List command
To list assets applications or models, use the command:

##### Default of 10 assets
  ```bash
  pieces list
  ```

##### Lists your x most recent assets
  ```bash
  pieces list assets x
  ```

##### Lists all registered applications
  ```bash
  pieces list apps
  ```

##### Lists all accessible AI models 
  ```bash
  pieces list models
  ```


##### Open an asset:

Opens an asset from a list or search. If only "open" is used then it will open your most recent asset. This also creates a link to the asset's code.

```bash
pieces open [ITEM_INDEX] [-e]
```

```-e``` is an optional flag . It Opens the asset in the configured external editor. Editor of choice can be configured using config command.

##### Editor Configuration:

You can configure an external editor to open assets for editing. Use the following command to set your preferred editor:

```pieces config editor <editor_command>```

##### Save, Create, Edit, and Delete Assets

The save create edit and delete commands currently work on the current asset which is by defualt set to the most recent one and you can change the current asset to anything using the open command above.


##### Save the current asset:

You need to edit the snippet code that was opened via the open command `pieces open` then save the changes to using the save command

```bash
pieces save
```

##### Create a new asset:

Will take whatever text is copied to your clipboard and create an asset. The asset will automatically be scanned and recognized for it's file type. 

```bash
pieces create
```

##### Edit an existing asset:

This will edit the name and reclassify the current asset.

```bash
pieces edit
```
This is used to edit both the classification and name of an asset.


```bash
pieces edit --name "new name"
```
to edit the name

```bash
pieces edit --classification python
```
to edit the classification


You can you -n or -c to change the name and classification respectively with the edit command.

##### Delete an asset:

This will delete an opened asset by using list or search first. If you do not have an opened asset it will open your most recent asset and ask if you'd like to delete it. 

```bash
pieces delete
```
##### clear:

this will clear the terminal and you will stay in the cmd loop and give you clean terminal interface. 

```bash
pieces clear
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

**Note**: For the larger queries , enclose the query in quotes.

##### change the llm model you are using:

Change the model in the ask command.

```bash
pieces change_model [MODEL_INDEX]
```
##### Conversations command
###### Coversations

List all conversations that you have. The green conversation is the one that is currently being used in the ask command

```bash
pieces conversations
```

###### Conversation

List the messages in the currently using conversation in the ask command. 

```bash
pieces conversation
```

You can create a new conversation that will be used in the ask command.

```bash
pieces conversation -n
```

Rename a conversation

```bash
pieces conversation -r My awsome name
```

Or you can make the model rename it for you

```bash
pieces conversation -r
```

Delete a conversation

```bash
pieces conversation -d
```



You can switch the conversation and list its messages. Check the conversations command to get the index

```bash
pieces conversation x
```


##### Ask a question to a model:
**Requires quotes around question**

Ask the Pieces Copilot a question. You can add a relevant file, you can also add relevant snippets based on their index shown in the assets list command. In order to change models from the default (GPT3.5), use the `change_model` command You can add a relevance file or snippet index check the `list assets` command.
You can use `.` or `/` to refer to the current directory 

```bash
pieces ask "your question" -f /file1 /file2 folder -s 1 2 3
```




##### Commiting to github

Auto commit the code to github and generate a commit message you can use the `-p` or `--push` flags to push the code to the repo too.

```bash
pieces commit -p
```

You can also add the `-i` or `--issues` flags so the commit message will include the issue numbers in the commit if found one else it will list all the issues to choose from.

```bash
pieces commit -i
```

#### Login and logout 
Login to pieces 

```bash
pieces login
```

Logout from pieces 

```bash
pieces logout
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


### Installation
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
pip install pieces-cli-{VERSION}-py3-none-any.whl 
```
replace the VERSION with the version you downloaded
Note: Ensure you get latest from the [releases](https://github.com/pieces-app/cli-agent/releases) of the cli-agent


11. To view all the CLI Commands
```shell 
pieces help 
``` 

these can be local/github/pypi etc.


### Updating
To update the project, run the following command:

```shell
pip install pieces-cli --upgrade
```


### Testing
To discover and run all the test cases in the repository, run the following command:

```shell
pytest
```

To check the test coverage, you can use the coverage package. Install coverage with:
```shell
pip install coverage
```

Run the tests with coverage using the following command:
```shell
coverage run -m pytest
coverage report
```

### Uninstallation
To uninstall the project, run the following command:

```shell
pip uninstall pieces-cli
```
Don't forget to remove the virtual environment and dist folder

