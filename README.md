# Glued
## A CLI tool for developing and deploying AWS glue jobs
### VERSION 0.2.0

# Getting Started
```
pip install glued
```

## Create a Project
```
glued project init
```

## Create a New Job
```
glued job new <job-name>
```

### Job Directory Structure
```
glue_jobs
    my_job
        jars       -- put your job java dependencies here
        py         -- put your python dependencies here
        .version   -- file used to track diff between local and s3
        config.yml -- holds the aws glue job execution configuration
        main.py    -- the main entry point for the glue job
```



## Deploy Jobs
