# Phoebe Shelves Command Line Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Example image of Phoebe Shelves CLT in use](https://github.com/anthony-agbay/phoebe-shelves-clt/blob/main/img/phoebe-shelves-clt-example.png)

Phoebe Shelves is reading management tool based on 1) a book database and 2) a reading database. The command line tools provides tools for managing these databases. Currently, the tools support the following actions:

- Adding, editing, and removing entries from both databases
- Automatic calculation of the time for each reading event (days)
- Automatic calculation of total number of times you have read a book
- Support for multiple book ratings and an average rating
- Visualization of the databases on the command line

## Instructions

The following provides an overview of how to use the script. Currently, the tools are unavailiable via PyPI, but you can utilize the scripts by cloning the repository to your device or downloading the latest stable version from the releases section.

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

##### Choosing a Backend Model

Phoebe Shelves CLT supports two data models: a PostgreSQL database and CSV files. Both models should support the same core features, so there is no inherent advantage to either approach. In the future, the PostgreSQL backend may integrate with remote locations/servers more easily, however.

If you choose to use the CSV backend, there are no further dependencies to install. If you choose to use the PostgreSQL backend, make sure to [intall PostgreSQl](https://www.postgresql.org/download/) and ensure the server is running.

#### 2. Installing Script

Because a public release on pip has not been completed, you will have to install the script manually. Once you have cloned the directory/downloaded the latest release to your local computer, navigate to the directory on the command-line and install the package manually using the following line:

```console
pip install .
```

#### 3. Setting Up Configurations

The script relies on a configuration file (`config.cfg`) located in the `phoebeshelves` folder. This configuration file stores a variety of configurations for the script. To setup the configuration file, you use the included `config` tool:

```console
// Initialize configuration using the default data directory path
$ phoebeshelves config

// Print out the current list of configurations
$ phoebeshelves config check

// Modify a configuration
$ phoebeshelves config [config_name] [new_value]
```

For a list of the arguments to modify the configurations, pass:

```console
$ phoebeshelves config -h
```

#### 3. Initializing Databases

Once you are done configuring the data directory path, the next step is to initialize the backend model.

```console
$ phoebeshelves init
```

If any of the backend model files already exist, this call will *not overwrite any of the existing data*. If you want to overwrite existing files, pass the `-f` flag.

```console
$ phoebeshelves init -f
```

### Viewing and Managing the Databases

There are two primary tools for working with the databases: "view" and "manage" mode. The modes can be quickly activated by passing in the appropriate arguments:

```console
$ phoebeshelves view [database] [mode]

$ phoebeshelves manage [database] [mode]
```

Each tool provides interactive prompts for the remainder of the script.

#### Viewing the Databases

There are three primary modes for viewing the database: 1) printing a table to the command line, 2) generating charts of the database, and 3) generating summary statistics. **Currently, only printing the database is fully implemented.**

```console
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

```console
// Add new entry to the books database
$ phoebeshelves manage books add

// Edit an entry in the books database
$ phoebeshelves manage books edit

// Delete an entry in the reading database
$ phoebeshelves manage reading delete
```