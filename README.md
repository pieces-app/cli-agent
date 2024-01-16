# Pieces Python CLI Tool
This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with Pieces OS. It provides a range of functionalities such as asset management, application interaction, and integration with various Pieces OS features.

## Website • Documentation

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

For instance - open instead of pieces open

If you have a numbered list or search open you can just type the number and it will open the asset associated. 

```bash
  pieces run
  ```

#### List Assets
- To list assets or applications, use the command:

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
pieces search query
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

Examines all words in a document to find matches to search criteria

##### Ask a question to a model:

This currently only supports GPT 3.5 and it does not have working memory. Only coding questions are currently supported. To use the model's code you can copy it from the console and use the create command to create an asset using the copied code. 

```bash
pieces ask "your question"
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