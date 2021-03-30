# Owl Shelves Command Line Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Owl Shelves is reading management tool based on 1) a book database and 2) a reading database. The command line tools provides tools for managing these databases as a pair of CSV files via the command line. Currently, the tools support the following actions:

- Adding, editing, and removing entries from both databases
- Automatic calculation of the time for each reading event (days)
- Visualization of the databases on the command line

**Note: There current build is under active development and likely still contains bugs and/or result in data loss. Please only use for testing purposes** A stable version will be released via the releases tab or via PyPI when ready.

## Instructions

The following provides an overview of how to use the script. Currently, the tools are unavailiable via PyPI. You can download scripts by cloning to your device.

### General Usage

To run the script, the primary python file is `code/core.py`

```python
python3 code/core.py <modes> <optional-flags>
```

### Installation and Configuration

#### 1. Installing Dependencies

Owl Shelves has the following dependencies:

- [Pandas](https://pandas.pydata.org)
    - `pip install pandas`
    - `conda install pandas`
- [tabulate](https://pypi.org/project/tabulate/)
    - `pip install tabulate`
    - `conda install tabulate`

#### 2. Setting Up Configurations

The script relies on a configuration file (`configs.conf`) located in the `code` folder. This configuration file only stores the path to the data directory that will store the CSV files. To setup the configuration file, you can use the included `config` option:

```shell
# Initialize configuration using the default data directory path
python3 code/core.py config

# Initialize configuration using a custom data directory path
python3 code/core.py config -d <path_to_custom_directory>
```

To modify the path afterwards, use the second option above.

#### 3. Initializing Databases

Once you are done configuring the data directory path, the next step is to initialize the CSV files. This can be done via the following:

```shell
python3 code/core.py init
```

If there is already an existing `books.csv` or `reading.csv` in the target directory, you can do the following to force overwrite the files:

```shell
python3 code/core.py init -f
```

### Viewing and Managing the Databases

There are two primary modes for working with the databases: "access" and "manage" mode. The modes can be quickly activated by passing in the appropriate arguments:

```shell
python3 code/core.py view <optional-flags>

python3 code/core.py manage <optional-flags>
```

#### Viewing the Databases

Currently, the tools only support printing a markdown-formatted visualization of the databases to the command line.

```shell
# View Reading Database
python3 code/core.py view -rd

# View Books Database
python3 code/core.py view -bd
```

#### Managing the Databases

Mangaging the databases occurs through interactive prompts via the command line. Once you enter a management flow, you can pass the keyboard interrupt "Ctrl-C" to gracefully exit.

```shell
# Enter management mode for the reading database
python3 code/core.py manage -rd

# Enter management mode for the book database
python3 code/core.py managed -bd
```
