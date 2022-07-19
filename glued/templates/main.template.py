import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job


def main() -> None:

    expected_args = ["JOB_NAME"]
    args = getResolvedOptions(sys.argv, expected_args)

    spark_context = SparkContext.getOrCreate()
    glue = GlueContext(spark_context)
    spark = glue.spark_session

    # Init the glue job
    glue_job = Job(glue)
    glue_job.init(args["JOB_NAME"], args)

    # mode code here....


if __name__ == "__main__":
    main()
