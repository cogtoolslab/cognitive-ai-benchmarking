To configure your environment for using CAB, you will need to create a config file.  This file is in the INI format (https://en.wikipedia.org/wiki/INI_file).  The location of the file is, by default [YOUR_HOME_DIR]/.cabconfig, but you can specify the location of this file with the enviroment variable CAB_CONFIGFILE.

Currently, this config file contains information about credentials and variables to access the mongodb used for stimulus and result storage.   See below for an example for what the contents of this file should look like.  

##########example contents for .cabconfig file

[DB]

password=mypassword #required. this is the password for your database user

username=myusername #optional, default if unspecified is "cabUser"

host=myhost #optional, default if unspecified is 127.0.0.1

port=myport #optional, default if unspecified is 27017
