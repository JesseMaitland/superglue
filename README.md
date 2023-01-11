# Superglue
## A CLI tool for developing, testing and deploying AWS glue jobs
### VERSION 0.10.0

Superglue makes the development, troubleshooting and deployment of AWS glue jobs simple. It also makes creating a shared 
glue codebase easy and testable


# Getting Started
```
pip install superglue
```

### Create a Superglue Project

Superglue is intended to be used for a "project" or "collection" of AWS glue jobs. To create a superglue project run
```
superglue init
```

### Project Structure
```
jobs        -- all of your glue jobs live here
modules     -- shared glue code lives here
notebooks   -- jupyter notebooks live here
tests       -- where your tests for jobs and modules go
tools       -- holds the superglue makefile can be used for other scripts and snippets
makefile    -- used as a master makefile. Includes tools/makefile
.env        -- the environment vars needed to make superglue tick
.gitignore  -- a templated .gitignore to get you started
```

### The Superglue Job 
A superglue job is a directory which contains your job's `config.yml` file, as well as a `main.py` entrypoint, `jarfile` dependencies,
other python scripts, and deployment info about the job.

```
superglue new job --name <your job name>
```

#### Job Directory Structure

```
jobs
    my_job
        jars           -- put your job java dependencies here (optional)
        py             -- put your python dependencies here   (optional)
        config.yml      -- holds the aws glue job execution configuration
        overrides.yml  -- used to create multiple instances of your job (optional)
        deployment.yml -- holds the job deployment configuration 
        main.py        -- the main entry point for the glue job
        .version       -- file used to track diff between local and s3
```

#### Developing Your Job
Your job can now be developed using your desired IDE. At anytime you can check the packaging status
of your job by running `superglue status`


### Locking Your Job
Before a job can be deployed, it must be locked by superglue. Once the job is locked, it will be assigned a version number
which will auto-increment each time the job is locked. This number is more or less arbitrary, however it is used to keep previous
versions of your job available in AWS S3.

```
superglue lock
```

#### Config.yml
The `config.yml` file is where the base parameters for your glue job configuration will live. Any parameter that can be passed to the 
boto3 glue client can be included in this config file. 

Environment variable expansion is also supported. So you can do things like
```yaml
ScriptLocation: s3://some-bucket-${SOME_ENV_VAR}-path
```

Where the value for `${SOME_ENV_VAR}` will be taken from your machine's environment. 

#### Overrides.yml
This file is intended to make instances of your glue job with overridden properties possible and is used in the following way.
Values in `config.yml` will be overridden by whatever you put in here, with the `config.yml` used as the base. In this sense you can think
of this as an inheritance relationship where `overrides.yml` contains the children of `config.yml`
```yaml
overrides:
  - Name: heavy_workers
    NumberOfWorkers: 20
  - Name: light_workers
    NumberOfWorkers: 2
```

In the above example, 2 jobs will be created using the base parameters found in `config.yml` and the overridden values of 
`Name: ` and `NumberOfWorkers: ` will be used to create the `deployment.yml` file. 



### Deploying a Superglue Job
Once you are satisfied with your glue job, you can then deploy it on AWS. Just run
```
superglue deploy
```

This will upload your code to S3 to the configured locations, as well as create the glue job definition in AWS Glue. 


## Superglue Modules (Shared Glue Codebase)
AWS glue allows importing python modules that have been uploaded to s3, zipped in the appropriate structure, and have been added to the `--extra-py-files` argument. 
Manually managing these dependencies is difficult and error-prone. `superglue` allows you to create, package, 
and include shared code in your glue jobs in the following way. 

### Create a new module

All code which is shareable across superglue jobs lives in the `/modules` directory. 

```
superglue new module --name <your module name>
```

### Module Directory Structure
```
modules
    my_module_code          -- the parent directory for your module              
        my_module_name      -- your code lives here. This is the zipfile's root directory
            __init__.py     -- required for the zip archive
        .version            -- used by superglue to track changes
        my_module_name.zip  -- zip archive used by the glue job itself
```

### Locking a Superglue Module
Superglue modules must be locked before they can be packaged and deployed. Once locked, they will be assigned a version 
number which will be auto incremented. This number is arbitrary, however allows for keeping multiple versions of your modules in S3
to allow jobs which may use a previous version to still function.

```
superglue lock
```

### Packaging a Superglue Module
Superglue modules need to be packaged into a zip archive before they can be used by AWS glue. To do this run
```
superglue package
```

### Using a Superglue Module in a Glue Job
To include a module in your superglue job, simply add the module name to the `superglue_modules` section in
your job's `config.yml` file along with the version number you want to use.  
```
superglue_module:
    module_name:
       version_number: <integer value version number>
```

This code will now be importable in your glue job.
```python
from my_module import foo_bar # in this case, my_module is the name of the zipfile archive
```

## The Superglue Makefile
After running `superglue init` 2 makefiles were created. One in the root directory `makefile` and one in 
`tools/makefile`

The `makefile` in your projects root directory is intended to be used to add whatever custom automation
to your project that you like, and not clutter up the superglue makefile itself. By default, it will include
the superglue makefile at `tools/makefile`

From the project's root directory, you can run `make help`

### AWS Glue Docker Image (Official AWS)
For local development and testing of your superglue jobs and modules, you can pull the official AWS glue docker
image from docker hub by running
```
make pull
```

### IDE Autocomplete
To allow your IDE to make auto complete suggestions, we need to include the AWS glue source code in project venv.
To do this just run
```
make glue
```
This will clone the `aws-glue-libs` project from github into the `/tools` directory, copy the `awsglue` source code into
your `venv` and remove the repo once completed. Your IDE autocomplete engine should automatically index this
and make suggestions for you during local development


## Superglue Testing
All superglue tests can be found in the `/tests` directory. These tests get mapped into the docker container and run
by using the `make test` command. All tests are run in the docker container using `pytest` 

All import paths are included on the `PYTHONPATH` automatically. All superglue jobs and modules should be 
directly importable. 

To tests superglue modules, they must first be packaged. Before running `make test` you must run `superglue package`
This will ensure that the actual zip archive is being tested, which is what your glue job will actually be using.
