# Phoebe Shelves Command Line Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Example image of Phoebe Shelves CLT in use](https://github.com/anthony-agbay/phoebe-shelves-clt/blob/main/img/phoebe-shelves-clt-example.png)

Phoebe Shelves is reading management tool based on 1) a book database and 2) a reading database. The command line tools provides tools for managing these databases as a pair of CSV files via the command line. Currently, the tools support the following actions:

- Adding, editing, and removing entries from both databases
- Automatic calculation of the time for each reading event (days)
- Automatic calculation of total number of times you have read a book
- Support for multiple book ratings and an average rating
- Visualization of the databases on the command line

**Note: There current build is under active development and likely still contains bugs and/or result in data loss. Please only use for testing purposes** A stable version will be released via the releases tab or via PyPI when ready.

## Instructions

The following provides an overview of how to use the script. Currently, the tools are unavailiable via PyPI, but you can utilize the scripts by cloning the repository to your device.

### General Usage

There are two types of tools: script configuration and database management.

```console
$ phoebeshelves [tool] [arguments]
```

At any point during the interactive prompts, you can utilize Ctrl-C or Ctrl-D to safely close the program without modifying any files.

### Installation and Configuration

#### 1. Installing Dependencies

Phoebe Shelves has the following dependencies:

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

#### 2. Installing Script

Because a public release on pip has not been completed, you will have to install the script manually. Once you have cloned the directory to your local computer, navigate to the directory on the command-line and install the package manually using the following line:

```console
pip install .
```

#### 3. Setting Up Configurations

The script relies on a configuration file (`config.cfg`) located in the `phoebeshelves` folder. This configuration file only stores the path to the data directory that will store the CSV files. To setup the configuration file, you can use the included `config` tool:

```console
// Initialize configuration using the default data directory path
$ phoebeshelves config

// Initialize configuration using a custom data directory path
$ phoebeshelves config -u [path_to_custom_directory]
```

To modify the path afterwards, use the second option above.

#### 3. Initializing Databases

Once you are done configuring the data directory path, the next step is to initialize the CSV files. This can be done via the following:

```console
$ phoebeshelves init
```

If there is already an existing `books.csv` or `reading.csv` in the target directory, it ask you to confirm if you would like to overwrite the files. If you want to overwrite existing files without confirmation, pass the `-f` flag.

```sh-session
$ phoebeshelves init -f
```

### Viewing and Managing the Databases

There are two primary tools for working with the databases: "view" and "manage" mode. The modes can be quickly activated by passing in the appropriate arguments:

```sh-session
$ phoebeshelves view [database] [mode]

$ phoebeshelves manage [database] [mode]
```

Each tool provides interactive prompts for the remainder of the script.

#### Viewing the Databases

There are three primary modes for viewing the database: 1) printing a table to the command line, 2) generating charts of the database, and 3) generating summary statistics. **Currently, only printing the database is fully implemented.**

```sh-session
// Printing the books database as a table
$ phoebeshelves view books table

// Generating charts of the reading database
$ phoebeshelves view reading charts

// Calculate summary stats of the reading database
$ phoebeshelves view reading stats
```

For all modes, you will be prompted to optionally filter the database based on the column data, such as the start or finish date in the reading database. If decide to filter a database, this filtered database will be used for the remainder of the script rather than the original database.

#### Managing the Databases

There are three primary actions for managing the database: 1) adding a new entry, 2) editing an existing entry, and 3) deleting an existing entry.

```sh-session
// Add new entry to the books database
$ phoebeshelves manage books add

// Edit an entry in the books database
$ phoebeshelves manage books edit

// Delete an entry in the reading database
$ phoebeshelves manage reading delete
```