# you can run this code with "source jupyter_setup.sh"
#change this public DNS address to the address of your spark master node
export spark_master_hostname=ec2-18-191-239-57.us-east-2.compute.amazonaws.com

export memory=11000M 

export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.7-src.zip:$PYTHONPATH

PYSPARK_DRIVER_PYTHON=jupyter PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=7777" pyspark --master spark://$spark_master_hostname:7077 --executor-memory $memory --driver-memory $memory
