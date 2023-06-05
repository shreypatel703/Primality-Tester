# Primality Tester
This project uses Fermat's Little Theorem for testing the primality of an integer. I've implemented the theorem in three different ways, each version get more complex and efficient than the other.

# Project Status
Versions 1 and 2 have been completed, but version 3 is currently under development.

# Installation and Setup Instructions
Clone down this repository. You will need python3, and the Click library

Navigate to either the version1 or version2 folder:
`cd version1`
or
`cd version2`

Run the following command to run the manager:
`python3 primey/manager/__main__.py --host localhost --port 6000 --logfile var/log/primey-server.log --loglevel=DEBUG`

(Version 2 only) Run the following command to run the workers:
`python3 primey/worker/__main__.py --host localhost --port 6001 --manager-host localhost --manager-port 6000 --logfile var/log/mapreduce-worker-6001.log --loglevel=DEBUG`
`python3 primey/worker/__main__.py --host localhost --port 6002 --manager-host localhost --manager-port 6000 --logfile var/log/mapreduce-worker-6002.log --loglevel=DEBUG`
**Note:** To add more workers, you can use the same command, just change the --port option to an unused port number

# Running Tests
To run a provided test run the following command:
`python3 Tests/filename.py`
Example:
`python3 Tests/test1.py`

To add more tests simply use the structure of the provided test file.

# Version 1:
Version 1 is a very basic implementation of the primality tester. Upon initialization, a TCP server is started through which new jobs are submited.
A job must be a JSON object of the following format:
`{
    "message_type": "new_job",
    "n": "13",
    "output_directory": tmp_path,
}`

Here "n" is the number that we are trying to determine is prime and the "output_directory" is the location of where the final output file will be saved.

Once the new job order has been received, the manager will perform all calculations by itself. Once complete the outcome will be saved to a file in the given ouput directory.

# Version 2
Version 1 works perfectly fine for small integers, however; once we get to larger numbers, the process manager takes too long doing all the work by itself.

That is why in Version 2, we now introduce workers. Instead of attempting to do all the checking by itself, the manager now hands off the calculations to the workers. 

### Step 1: Worker Initialization
When a new worker is initialized, it will send a registration message to the manager at the given port. Once the manager recieves this message, the manager adds the worker to its list of workers and returns an registration acklowledgement.

### Step 2: Task distribution
When the manager recieves a new job, it will begin to assign tasks to any free workers through the TCP channel. If no worker is free, it will wait until one opens up. 
Once a worker completes its given task, it will return a completion message to the manager.

### Step 3: Output Results
Once all tasks have been, completed the manager will save the output to the given given location.

## Worker Heartbeat
To ensure that that workers remain healthy and no work is lost, workers are required to send a UDP heartbeat message every 2 seconds. If the manager does not receive a heartbeat from the worker for more than 10 seconds, the worker will be registered as dead, and will not be sent any tasks.
