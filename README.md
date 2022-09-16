# Superglue
## A CLI tool for developing and deploying AWS glue jobs
### VERSION 0.3.0

Superglue is intended to make the development, troubleshooting and deployment of AWS glue jobs simple.

AWS glue is a powerful technology and is great for processing medium-sized datasets into your datalake, however
deployment, deployment and testing of glue jobs is far less straight forward. We hope that `superglue` will make working
with aws glue simpler than ever for you.

# Getting Started
```
pip install superglue
```

### Create a Superglue Project

Superglue expects a few directories and files to exist, and be named in a certain way. In this regard, you could say 
`superglue` is opinionated.

```
superglue project init
```

### Create a New Job
A superglue job is really just the job definition file, as well as your code all in one place (directory) To create a job
simply run the command 

```
superglue job new <job-name>
```

#### Job Directory Structure
```
glue_jobs
    my_job
        jars       -- put your job java dependencies here
        py         -- put your python dependencies here
        .version   -- file used to track diff between local and s3
        config.yml  -- holds the aws glue job execution configuration
        main.py    -- the main entry point for the glue job
```

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




