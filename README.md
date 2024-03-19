# python-scripts

In this repository, there are scripts I have created that run various tasks using Python.

<hr/>

<b>File-Check.py:</b> This python script runs a check on a directory and its working tree,<br/>
then runs a check on those files to see if they have been within the directory for more than a specified time,<br/>
if they are, log this info to a file in a basic fashion.

<hr/>

<h2>Run a script as a service:</h2>
To run any script as a service/daemon in a linux machine,<br/>
I attached a mock service file that must be added into your systemd file system<br/>
to run this script in the background, configure the file as needed.

On your linux machine (with admin previleges), navigate from the root directory to:

```
cd /lib/systemd/system
```

Then you will create a file within this directory (use whatever editor you are comfortable with).<br/>
Then copy the contents of the fileCheck.service file in my repository to the file you just created.<br/>
You must edit this line in the file to include the necessary arguments to run the python script


> /path/to/script/name_of_script.py "fileCheck" -d "/path/to/DirectoryToWatch/" -lf "/path/to/logfile/name-of-file.*"<br/>
> -ef "/path/to/excludeFile/name-of-file" --interval NumofSecs(int) -exp "/path/to/expirey-folder" -meta "/path/to/meta-file"


I will explain the arguments(abbreviations explained as well):<br/>
<b>path/to/script/name_of_Script/py:</b> Where fileCheck.py resides on your machine.<br/>
<b>-d (--directory):</b> The directory fileCheck.py will perform on.<br/>
<b>-lf (--log-file):</b> The location of your log file.<br/>
<b>-ef (--exclude-file):</b> The location of your exclusion list.<br/>
<b>-i (--interval):</b> How often (in seconds) should fileCheck.py execute.<br/>
<b>-exp (--expired-folder):</b> The location of the expired folder.<br/>
<b>-meta (--meta-file):</b> The location of your metadata file.<br/>

I explain the functions of these further in fileCheck.py in the comments at the very top.

> [!TIP]
> I recommend you have all files and directories under one main directory for simplicity.

<hr/>

<h2>How to test the script:</h2>
To test the fileCheck.py script, I have created a test script.<br/>
This test is using Pytest testing framework to aid in testing the script before deploying to a production environment.<br/>
The test script fileCheck_test.py uses a built-in library called unittest,<br/>
& it a creates mock directory to test the functionality of the code!<br/>
To run the test, make sure the fileCheck.py & fileCheck_test.py are in the same directory and run the following:


```
python3 fileCheck_test.py
```

To run the test against the fileCheck using pytest, you must:
 
 - You must install the pytest framework using the pip installation package
 - use pytest CLI commands to run the test (preferably have both scripts in the same directory)

Pip installation (Linux & with admin permissions):
```
apt install python3-pip
```

PyTest installation (Linux & with admin previleges):
```
pip install pytest
```

PyTest script run command:
```
pytest name_of_test_script_test.py
```

> [!NOTE]  
> It is a good practice to name the test script after the script you are running the test on,<br/>
>followed by "_test.py", to allow you to search for pytest scripts efficiently when needed.
