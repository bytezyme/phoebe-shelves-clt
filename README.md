# Owl Shelves Command Line Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![](https://github.com/anthony-agbay/owl_shelves_clt/blob/main/img/owl-shelves-clt-example.png)

Owl Shelves is reading management tool based on 1) a book database and 2) a reading database. The command line tools provides tools for managing these databases as a pair of CSV files via the command line. Currently, the tools support the following actions:

- Adding, editing, and removing entries from both databases
- Automatic calculation of the time for each reading event (days)
- Visualization of the databases on the command line

**Note: There current build is under active development and likely still contains bugs and/or result in data loss. Please only use for testing purposes** A stable version will be released via the releases tab or via PyPI when ready.

## Instructions

The following provides an overview of how to use the script. Currently, the tools are unavailiable via PyPI. You can download scripts by cloning to your device.

### General Usage

```console
owl_shelves_clt <mode> <optional-flags>
```

### Installation and Configuration

#### 1. Installing Dependencies

Owl Shelves has the following dependencies:

- [pandas](https://pandas.pydata.org)
    - `pip install pandas`
    - `conda install pandas`
- [numpy](https://numpy.org/)
    - `pip install numpy`
    - `conda install numpy`
- [matplotlib](https://matplotlib.org/stable/index.html)
    - `pip install matplotlib`
    - `conda install matplotlib`
- [tabulate](https://pypi.org/project/tabulate/)
    - `pip install tabulate`
    - `conda install tabulate`

#### 2. Setting Up Configurations

The script relies on a configuration file (`config.cfg`) located in the `owl_shelves_clt` folder. This configuration file only stores the path to the data directory that will store the CSV files. To setup the configuration file, you can use the included `config` option:

```console
# Initialize configuration using the default data directory path
owl_shelves_clt config

# Initialize configuration using a custom data directory path
owl_shelves_clt config -d path_to_custom_directory>
```

To modify the path afterwards, use the second option above.

#### 3. Initializing Databases

Once you are done configuring the data directory path, the next step is to initialize the CSV files. This can be done via the following:

```console
owl_shelves_clt init
```

If there is already an existing `books.csv` or `reading.csv` in the target directory, it will not overwrite the files without confirmation. To force-overwrite exsiting files, pass the additional `-f` argument:

```console
owl_shelves_clt init -f
```

### Viewing and Managing the Databases

There are two primary modes for working with the databases: "view" and "manage" mode. The modes can be quickly activated by passing in the appropriate arguments:

```console
owl_shelves_clt view <optional-flags>

owl_shelves_clt manage <optional-flags>
```

If no optional flags are passed, then an interactive prompt will guide you through options for interacting with the databases.

#### Viewing the Databases

There are three primary actions for viewing the database: 1) printing the database to the terminal, 2) graphing the database using different charts, and 3) analyzing the database for aggregate information. **Currently, only printing the database is fully implemented.**

There are two sets of optional arguments that can be passed when using the viewing mode: 

- `-rd/-bd`: Use the reading database or books database, respectively
- `-m <print/graph/analyze>`: Enter the print, graph, or analyze actions instead of following the interactive prompt

```console
// Directly enter analyze action on the reading database
owl_shelves_clt view -rd -m analyze
```

#### Managing the Databases

Mangaging the databases occurs through interactive prompts via the command line. Once you enter a management flow, you can pass the keyboard interrupt "Ctrl-C" to gracefully exit.

```console
# Enter management mode for the reading database
python3 code/core.py manage -rd

# Enter management mode for the book database
python3 code/core.py managed -bd
```
