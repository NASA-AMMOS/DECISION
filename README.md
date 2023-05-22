# DECISION
DECISION Ground on the Loop Autonomy Planning Tool

## Conda Environment
DECISION uses Conda to maintain dependancy versions.  Follow the instruction [`here`](envs/README.md) to set up the DECISION conda environment.

## Submodules
Run the follow commands to recursively collect and update submodules.
```bash
cd DECISION
git submodule init
git submodule update --recursive
```
If encountering an error, download the submodule directly from the repository (https://github.com/JPLMLIA/OWLS-Autonomy.git) and put it in `decision/OSIA/OWLS-Autonomy/`

## Building the ACME OSIA Docker container
DECISION runs the ACME OSIA algorithm inside a docker container.  To build this container run the following commands.
```bash
cd DECISION/decision/OSIA/OWLS-Autonomy/
docker build . -f Dockerfile_ACME --tag owls-autonomy-acme:v1
```

## Increasing Docker Memory
Default RAM allocated to Docker containers can be too low if you're attempting to optimize many ACME observations at once. RAM allocation can be increased from the Docker desktop application under gear icon->Resources->Memory.  We recommend running the ACME Docker container with 10-12GB of RAM if your system allows.

## DECISION Demo Data
Demo data to use with DECISION can be found at https://ml.jpl.nasa.gov/projects/decision/ACME_Demo_Data.zip. Unzip this repository and place it in DECISION/decision/data/.

## Installing Dakota
DECISION utilizes Dakota for parameter optimization. Follow instructions at https://dakota.sandia.gov/content/install-dakota-0 to install Dakota.

## Testing DECISION
Verify installation by running DECISION unit tests.  This is accomplished with the following commands. Test coverage reports will be generated in docs/coverage_report/. View docs/coverage_report/index.html for a summary of testing results.
```bash
cd DECISION/decision/
pytest -rP --ignore=OSIA --disable-warnings --cov=decision --cov-report html:docs/coverage_report test/ -v
```

## Running DECISION
Start DECISION using the following commands.
```bash
cd DECISION/decision/
python decision.py
```

From a web browser visit http://127.0.0.1:8050/ to see the DECISION application.  We recommend Google Chrome for optimal compatibility. 



### Copyright
Copyright 2023, by the California Institute of Technology. ALL RIGHTS RESERVED. United States Government Sponsorship acknowledged. Any commercial use must be negotiated with the Office of Technology Transfer at the California Institute of Technology.

This software may be subject to U.S. export control laws. By accepting this software, the user agrees to comply with all applicable U.S. export laws and regulations. User has the responsibility to obtain export licenses, or other export authority as may be required before exporting such information to foreign countries or providing access to foreign persons.
