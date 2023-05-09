
## Installing and Running the DECISION Conda Environment
 The `conda` program is an open source package and environment manager commonly used for Python, and operating at the core of the Anaconda Python distribution.  The YAML file(s) in this directory define a `conda` environment for running the DECISION python software.

### Installing and Updating Anaconda
Instructions on installing Anaconda are here: https://docs.anaconda.com/anaconda/install/.  Make sure Anaconda's `bin` directory is on your path before proceeding.

If Anaconda is already installed, but is not up to date, you can update it with the following commands (the first updates the `conda` program itself, the latter updates the python packages bundled with Anaconda):
```bash
$ conda update conda
$ conda update anaconda
```

### Creating the Conda Environment
Assuming you have an up-to-date version of anaconda installed, you can install or update the environments with the commands below.

```bash
$ cd $DECISION_REPO
$ conda env create -f envs/environment.yml
```

In the above example, the variable `$DECISION_REPO` is assumed to point to the DECISION repo root.

### Updating the Conda Environment
If the `environment.yml` file changes for any reason (e.g. adding new packages), the environment may be updated to be consistent with this new YAML file with the following command.

```bash
$ cd $DECISION_REPO
$ conda env update -f envs/environment.yml
```

In the above example, the variable `$DECISION_REPO` is assumed to point to the DECISION repo root.

### Usage
With Anaconda's `bin` directory on your path, you can activate the environment by typing `source activate decision` (the environment's name, `decision`, is defined at the top of the YAML file).  Once active, only the packages, and respective versions, installed into the environment will be available when running Python.

Exiting the environment is a simple `source deactivate` command at the command-line.

```bash
$ source activate decision
$ source deactivate
```

### Exporting an Environment

Once created, an environment's definition may be exported to a YAML file again.  The command to do this:
```bash
$ conda env export > environment.yml
```
This `environment.yml` file will contain all packages that were installed, which will be a superset on those originally provided, as it will include any dependencies needed by the packages specified in `environment.yml`.  It will also contain the exact version of the installed packages, (hopefully) allowing an environment to be perfectly reproduced on another machine.

## Adapted from ONWATCH enviornment documentation written by Steven Lewis.


