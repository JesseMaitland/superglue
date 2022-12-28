# Superglue
## A CLI tool for developing, testing and deploying AWS glue jobs
### VERSION 0.5.0

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
modules     -- shared glue code lives hwere
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
superglue job new --name <your job name>
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

### Deploying a Superglue Job
Once you are satisfied with your glue job, you can then deploy it on AWS. To do this, you must first package your job by running
```
superglue job package
```
This command will then create a version number for your job, as well as a hash value used to track the state
of the job. This can be found in the `.version` file in your job directory.

To deploy your job, now you need to simply run
```
superglue job deploy
```
This will do the following things 
1. Check that all jobs can be deployed
2. Upload all job files to S3
3. Create the job in AWS glue


## The Superglue Module
AWS glue allows importing python modules that have been uploaded to s3, zipped in the appropriate structure, and have been added to the `--extra-py-files` argument. 
Manually managing these dependencies is difficult and error-prone. `superglue` allows you to create, package, 
and include shared code in your glue jobs in the following way. 

### Create a new module

All code which is shareable across superglue jobs lives in the `/modules` directory. 

```
superglue module new --name <your module name>
```

#### Module Directory Structure
```
modules
    my_module_code          -- the parent directory for your module              
        my_module_name      -- your code lives here. This is the zipfile's root directory
            __init__.py     -- required for the zip archive
        .version            -- used by superglue to track changes
        my_module_name.zip  -- zip archive used by the glue job itself
```

Once you are happy with your module you can run
```
superglue module package
```

This will give your module a version number, and create a zip archive with the AWS glue expected
file / directory structure.

To include this module in your superglue job, simply add the module name to the `superglue_modules` section in
your job's `config.yml` file.  
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
