# Pieces Python CLI Tool
This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with Pieces OS. It provides a range of functionalities such as asset management, application interaction, and integration with various Pieces OS features.

## Website • Documentation

### Table of Contents
- [Operating System Support](#operating-system-support)
- [Installing](#installing)
- [Getting Started](#getting-started)
- [Usage](#usage)
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
2. Install the Python package using pip:

   ```bash
   pip install pieces-cli
   ```

#### Getting Started
After installing the CLI tool, you can access its functionalities through the terminal. The tool is initialized with the command `pieces` followed by various subcommands and options.

#### Usage

##### List Assets
- To list assets or applications, use the command:

  ```bash
  pieces list [options]
  ```
##### Open, Save, Create, Edit, and Delete Assets

##### Open an asset:

```bash
pieces open [ITEM_INDEX]
```

##### Save the current asset:

```bash
pieces save
```

##### Create a new asset:
```bash
pieces create
```

##### Edit an existing asset:

```bash
pieces edit
```

##### Delete an asset:

```bash
pieces delete
```

##### Search and Query
Perform a fuzzy search:

```bash
pieces search 'query' [--mode <search_type>]
```

##### Ask a question to a model:

```bash
pieces ask 'your question'
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
It is advised to keep the CLI tool updated to the latest version to ensure compatibility with Pieces OS and access to all features. Please refer to our documentation for details on supported versions.