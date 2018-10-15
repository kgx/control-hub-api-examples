# Start Control Hub Job with Custom Parameter Values

This example shows how to update the values of a Job's Parameters and to then launch it.

Set the ```Control Hub URL```, ```Job ID``` and ```params``` properties in the file ```bin/start-job-with-custom-params.sh```

Set your Control Hub credentials in the file ```private/sch_credentials.json```

Change to the ```bin``` directory and run ```./start-job-with-custom-params.sh``` and you should see output like this:

```
$ ./start-job-with-custom-params.sh
{"message":"Authentication succeeded"}Connecting to Control Hub at http://warsaw.onefoursix.com:18631
Retrieving  Job ID db26385e-2cf2-4e63-a52b-61369396cdc9:globex
The Job's existing Parameters are: '{"OUTPUT_DIR":"/tmp/out/dir45","FILE_PREFIX":"mark_45_"}'
Setting the Job's Parameters to the new value: '{"OUTPUT_DIR":"/tmp/out/dir100","FILE_PREFIX":"mark_100_"}'
Saving the modified Job on Control Hub
Starting the updated Job
Done
```
