# Pieces CLI Command Documentation

This document contains comprehensive documentation for all Pieces CLI commands.

_Generated automatically from command definitions_

## Table of Contents

- [ask](#ask)
- [chat](#chat) (aliases: conversation)
- [chats](#chats) (aliases: conversations)
- [commit](#commit)
- [config](#config)
- [contribute](#contribute)
- [create](#create)
- [delete](#delete)
- [edit](#edit)
- [execute](#execute)
- [feedback](#feedback)
- [install](#install)
- [list](#list) (aliases: drive)
- [login](#login)
- [logout](#logout)
- [onboarding](#onboarding)
- [open](#open)
- [run](#run)
- [save](#save) (aliases: modify)
- [search](#search)
- [share](#share)
- [version](#version)

## ask

Ask questions to the Pieces Copilot AI assistant with context from files, saved materials, or your long-term memory (LTM). Get intelligent code assistance and explanations

**Documentation:** [https://docs.pieces.app/products/cli#ask](https://docs.pieces.app/products/cli#ask)

### Examples

```bash
pieces ask 'how to implement a REST API'
```

```bash
pieces ask 'debug the main function' -f main.py utils.py
```

```bash
pieces ask 'What are these snippets about' -m 1 2 3
```

```bash
pieces ask 'What I was wroking on yesterday' --ltm
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `query` | str |  |  | Question to be asked to the Copilot |
| `--files, -f` | str |  |  | Folder or file as a context you can enter an absolute or relative path |
| `--materials, -m` | int |  |  | Materials of the question to be asked to the model check list materials |
| `--ltm` | str |  | False | Enable LTM for the current chat |

---

## chat

**Aliases:** `conversation`

Manage individual conversations with the Pieces Copilot. You can select, create, rename, or delete conversations

**Documentation:** [https://docs.pieces.app/products/cli#chat](https://docs.pieces.app/products/cli#chat)

### Examples

```bash
pieces chat
```

```bash
pieces chat 1
```

```bash
pieces chat --new
```

```bash
pieces chat --rename 'New Title'
```

```bash
pieces chat --renamepieces chat --delete
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `CONVERSATION_INDEX` | int |  |  | Index of the chat if None it will get the current conversation. |
| `-n, --new` | str |  | False | Create a new chat |
| `-r, --rename` | str |  |  | Rename the conversation that you are currently. If nothing is specified it will rename the current chat using the llm model |
| `-d, --delete` | str |  | False | Delete the chat that you are currently using in the ask command |

---

## chats

**Aliases:** `conversations`

Display a list of all your saved conversations with the Pieces Copilot, showing titles and timestamps for easy navigation

**Documentation:** [https://docs.pieces.app/products/cli#chats](https://docs.pieces.app/products/cli#chats)

### Examples

```bash
pieces chats
```

```bash
pieces chats 20
```

```bash
pieces conversations
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `max_chats` | int |  | 10 | Max number of chats to show |

---

## commit

Automatically generate meaningful commit messages based on your code changes using AI, with options to stage files, add issue references, and push to remote

**Documentation:** [https://docs.pieces.app/products/cli#commit](https://docs.pieces.app/products/cli#commit)

### Examples

```bash
pieces commit
```

```bash
pieces commit --push
```

```bash
pieces commit --all
```

```bash
pieces commit --issues
```

```bash
pieces commit -a -p
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `-p, --push` | str |  | False | Push the code to GitHub |
| `-a, --all` | str |  | False | Stage all the files before committing |
| `-i, --issues` | str |  | False | Add issue number in the commit message |

---

## config

Configure various Pieces CLI settings including default editor, API endpoints, and other preferences

**Documentation:** [https://docs.pieces.app/products/cli#config](https://docs.pieces.app/products/cli#config)

### Examples

```bash
pieces config
```

```bash
pieces config --editor vscode
```

```bash
pieces config --editor 'code --wait'
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--editor, -e` | str |  |  | Set the default code editor |

---

## contribute

Learn how to contribute to the Pieces CLI project, including guidelines for submitting pull requests, reporting issues, and improving documentation

**Documentation:** [https://docs.pieces.app/products/cli#contribute](https://docs.pieces.app/products/cli#contribute)

### Examples

```bash
pieces contribute
```

### Arguments

_No arguments_
---

## create

Create a new code snippet or material in your Pieces database. You can specify content directly or enter it interactively

**Documentation:** [https://docs.pieces.app/products/cli#create](https://docs.pieces.app/products/cli#create)

### Examples

```bash
pieces create
```

```bash
pieces create -c
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `-c, --content` | str |  | False | Specify the content of the material |

---

## delete

Permanently delete the currently selected material from your Pieces database. This action cannot be undone

**Documentation:** [https://docs.pieces.app/products/cli#delete](https://docs.pieces.app/products/cli#delete)

### Examples

```bash
pieces delete
```

### Arguments

_No arguments_
---

## edit

Edit properties of an existing material including its name, language classification, and other metadata

**Documentation:** [https://docs.pieces.app/products/cli#edit](https://docs.pieces.app/products/cli#edit)

### Examples

```bash
pieces edit
```

```bash
pieces edit --name 'New Name'
```

```bash
pieces edit --classification python
```

```bash
pieces edit -n 'API Handler' -c javascript
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--name, -n` | str |  |  | New name for the materials |
| `--classification, -c` | str |  |  | Reclassify a material |

---

## execute

Execute shell or bash code snippets directly from your saved materials, making it easy to run saved scripts and commands

**Documentation:** [https://docs.pieces.app/products/cli#execute](https://docs.pieces.app/products/cli#execute)

### Examples

```bash
pieces execute
```

### Arguments

_No arguments_
---

## feedback

Submit feedback, bug reports, or feature requests to help improve the Pieces CLI. Your feedback is invaluable for making the tool better

**Documentation:** [https://docs.pieces.app/products/cli#feedback](https://docs.pieces.app/products/cli#feedback)

### Examples

```bash
pieces feedback
```

### Arguments

_No arguments_
---

## install

Install or update PiecesOS, the local runtime that powers all Pieces applications. This command will download and set up PiecesOS for your platform

**Documentation:** [https://docs.pieces.app/products/cli#install](https://docs.pieces.app/products/cli#install)

### Examples

```bash
pieces install
```

### Arguments

_No arguments_
---

## list

**Aliases:** `drive`

List and browse various Pieces resources including code materials, connected applications, and available AI models. Use the editor flag to open snippets directly in your default editor.

**Documentation:** [https://docs.pieces.app/products/cli#list](https://docs.pieces.app/products/cli#list)

### Examples

```bash
pieces list
```

```bash
pieces list materials
```

```bash
pieces list apps
```

```bash
pieces list models
```

```bash
pieces drive
```

```bash
pieces list --editor
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `type` | str |  | materials | Type of the list |
| `max_snippets` | int |  | 10 | Max number of materials |
| `--editor, -e` | str |  | False | Open the choosen material in the editor |

---

## login

Authenticate with PiecesOS to enable cloud features, sync across devices, and access your personal workspace

**Documentation:** [https://docs.pieces.app/products/cli#login](https://docs.pieces.app/products/cli#login)

### Examples

```bash
pieces login
```

### Arguments

_No arguments_
---

## logout

Sign out from your PiecesOS account, disabling cloud sync and returning to local-only operation

**Documentation:** [https://docs.pieces.app/products/cli#logout](https://docs.pieces.app/products/cli#logout)

### Examples

```bash
pieces logout
```

### Arguments

_No arguments_
---

## onboarding

Start the interactive onboarding process to set up Pieces CLI, configure settings, and learn about key features through a guided tutorial

**Documentation:** [https://docs.pieces.app/products/cli#onboarding](https://docs.pieces.app/products/cli#onboarding)

### Examples

```bash
pieces onboarding
```

### Arguments

_No arguments_
---

## open

Open various Pieces applications and components including PiecesOS, Copilot, Drive, and Settings from the command line

**Documentation:** [https://docs.pieces.app/products/cli#open](https://docs.pieces.app/products/cli#open)

### Examples

```bash
pieces open
```

```bash
pieces open --pieces_os
```

```bash
pieces open --copilot
```

```bash
pieces open --drive
```

```bash
pieces open --settings
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `-p, --pieces_os` | str |  | False | Opens PiecesOS |
| `-c, --copilot` | str |  | False | Opens Pieces Copilot |
| `-d, --drive` | str |  | False | Opens Pieces Drive |
| `-s, --settings` | str |  | False | Opens Pieces Settings |

---

## run

Run the Pieces CLI in interactive loop mode, allowing you to execute multiple commands sequentially without restarting the CLI

**Documentation:** [https://docs.pieces.app/products/cli#run](https://docs.pieces.app/products/cli#run)

### Examples

```bash
pieces run
```

### Arguments

_No arguments_
---

## save

**Aliases:** `modify`

Save or update changes to the currently selected material. Use this after making modifications to persist your changes

**Documentation:** [https://docs.pieces.app/products/cli#save](https://docs.pieces.app/products/cli#save)

### Examples

```bash
pieces save
```

### Arguments

_No arguments_
---

## search

Search through your materials using various search modes including fuzzy search, neural code search, and full text search

**Documentation:** [https://docs.pieces.app/products/cli#search](https://docs.pieces.app/products/cli#search)

### Examples

```bash
pieces search
```

```bash
pieces search 'python function'
```

```bash
pieces search --mode ncs 'async await'
```

```bash
pieces search --mode fts 'TODO comments'
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `query` | str |  |  | Query string for the search |
| `--mode` | str |  | fuzzy | Type of search |

---

## share

Generate a shareable link for the currently selected material, allowing others to view and access your code snippet

**Documentation:** [https://docs.pieces.app/products/cli#share](https://docs.pieces.app/products/cli#share)

### Examples

```bash
pieces share
```

### Arguments

_No arguments_
---

## version

Display version information for both Pieces CLI and PiecesOS, including build numbers and compatibility details

**Documentation:** [https://docs.pieces.app/products/cli#version](https://docs.pieces.app/products/cli#version)

### Examples

```bash
pieces version
```

### Arguments

_No arguments_
---

## Additional Information

For more information about Pieces CLI, visit:
- [Pieces CLI Repository](https://github.com/pieces-app/cli-agent)
- [Pieces Documentation](https://docs.pieces.app/)
- [Pieces Website](https://pieces.app/)
