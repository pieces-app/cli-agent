![Pieces CLI for Developers](https://camo.githubusercontent.com/69c990240f877927146712d45be2f690085b9e45b4420736aa373917f8e0b2c8/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f7069656365735f7374617469635f7265736f75726365732f7066645f77696b692f5049454345535f4d41494e5f4c4f474f5f57494b492e706e67)
<p align="center">

# <p align="center"> Pieces Python CLI Tool

<p align="center"> This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with PiecesOS. It provides a range of functionalities such as asset management, application interaction, and integration with various PiecesOS features.

</p>
  
##### <p align="center"> [Website](https://pieces.app/) • [PiecesOS Documentation](https://docs.pieces.app/) • [Pieces Python CLI Documentation](https://docs.pieces.app/extensions-plugins/cli)
</p>

[![Introducing CLI](https://img.youtube.com/vi/kAgwHMxWY8c/0.jpg)](https://www.youtube.com/watch?v=kAgwHMxWY8c)

## Important

Make sure you have [**PiecesOS**](https://docs.pieces.app/products/meet-pieces/fundamentals) installed in order to run the Pieces CLI tool.

#### Operating System Support
The Pieces Python CLI Tool is compatible with various operating systems, ensuring a wide range of usage and adaptability. While it offers full support across most systems, specific features might have varied performance based on the OS environment.

The CLI Supports
- Windows 10 or greater
- Mac
- Windows

## Installing
To get started with the Pieces Python CLI Tool, you need to:

1. Ensure PiecesOS is installed and running on your system.
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

## Getting Started
After installing the CLI tool, you can access its functionalities through the terminal. The tool is initialized with the command `pieces` followed by various subcommands and options.


### Some important terminologies

- `x` -> The index
- `current asset` -> The asset that you are currently using can be changed by the open command 
- `current conversation` -> The conversation that you currently using in the ask command


## Usage

To refer to the list of all the commands currently supported in the Pieces CLI Agent, visit the [documentation](https://docs.pieces.app/extensions-plugins/cli/commands).

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

