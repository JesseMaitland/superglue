# Superglue
## A CLI tool for developing, testing and deploying AWS glue jobs
### VERSION 0.4.0

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
.env        -- the environment vars needed to make superglue tick
makefile     -- used as a master makefile. Includes tools/makefile
.gitignore  -- a templated .gitignore to get you started
```

### Create a New Job
A superglue job is a 

```
superglue job new --name <your job name>
```

#### Job Directory Structure
```
jobs
 my_job
     jars           -- put your job java dependencies here (optional)
     py             -- put your python dependencies here   (optional)
     .version       -- file used to track diff between local and s3
     config.yml      -- holds the aws glue job execution configuration
     overrides.yml  -- used to create multiple instances of your job (optional)
     deployment.yml -- holds the job deployment configuration 
     main.py        -- the main entry point for the glue job
```

#### Developing Your Job
You can now develop your job.

### Deploy a Job
`superglue` is intended to help automate the deployment and development process of glue jobs. To deploy a
single job to the AWS glue infrastructure, simply run

```
superglue job deploy <job-name>
```

## Sharing Code
AWS glue allows importing python modules that have been unloaded to s3, zipped in the appropriate structure, and have been added to the `--extra-py-files` argument. 
Manually managing these dependencies is difficult and error-prone. `superglue` allows you to create, package, 
and include shared code in your glue jobs in the following way. 

### Create a new shared module

All code which is shareable across modules lives in the `/shared` directory. 

```
superglue module new <module-name>
```

Adding a new shared module will create the following structure

```
shared
    my_module_code
        my_module_name
            __init__.py    
            " put your code files here "
        .version
        my_module_name.zip
```

Once you are happy with your module you can run
```
superglue module build <module-name>
```

This will give your module a version number, and create a zip archive with the AWS glue expected
file / directory structure.

To include this module in your jobs, simply add the module name to the `shared` key in `config.yml`
```
shared:
    - my_module
```

This code will now be importable in your glue job.

## Makefile
After running ``superglue project init`` a `makefile` was created. This file is intended to help automate your 
local aws development and testing environment. To see the available commands, please run
``make help``




