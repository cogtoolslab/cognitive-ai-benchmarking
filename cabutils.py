"""
CAB-level utils
"""
import sys
import os
import configparser
import pathlib
import pymongo as pm

#########################
########GENERAL##########
#########################

#load default settings
settings = configparser.ConfigParser()
this_dir = pathlib.Path(__file__).parent.absolute()
settings_file = os.path.join(this_dir,
                             "settings.conf")
settings.read(settings_file)

#expose several specific default settings
DEFAULT_CONFIG_FILENAME = settings['DEFAULTS']['CONFIG_FILENAME']
DEFAULT_MONGODB_PORT = settings['DEFAULTS']['MONGODB_PORT']
DEFAULT_MONGODB_HOST = settings['DEFAULTS']['MONGODB_HOST']
DEFAULT_MONGODB_USER = settings['DEFAULTS']['MONGODB_USER']

#load the user-level config file
#location of this file can be set by environment variable "CAB_CONFIGFILE"
#or it can be the default location ~/.cabconfig
if "CAB_CONFIGFILE" in os.environ:
    CONFIGFILE = os.environ["CAB_CONFIGFILE"]
else:
    CONFIGFILE = os.path.join(os.environ["HOME"],
                              DEFAULT_CONFIG_FILENAME)


_cab_configs = None
def get_cab_configs():
    """actually get the user-level cab configs
    """
    global _cab_configs
    if _cab_configs is None:
        if os.path.exists(CONFIGFILE):
            config = configparser.ConfigParser()
            config.read(CONFIGFILE)
            _cab_configs = config
        else:
            print("No config exists at path %s, check settings" % CONFIGFILE)
            sys.exit()
    return _cab_configs


#########################
########MONGODB##########
#########################

def get_db_port():
    """get db port, either from config file if specified, otherwise default
       to specify port in DB file, .cabconfig should have a section of the form:
       
       [DB]
           ...
       port=DESIRED_PORT
           ...
    """
    configs = get_cab_configs()
    if 'port' in configs['DB']:
        return configs['DB']['port']
    else:
        return DEFAULT_MONGODB_PORT


def get_db_host():
    """get db host, either from config file if specified, otherwise default
       to specify host in DB file, .cabconfig should have a section of the form:

       [DB]
           ...
       host=DESIRED_HOST
           ...
    """
    configs = get_cab_configs()
    if 'host' in configs['DB']:
        return configs['DB']['host']
    else:
        return DEFAULT_MONGODB_HOST


def get_db_user():
    """get db user, either from config file if specified, otherwise default
       to specify host in DB file, .cabconfig should have a section of the form:

       [DB]
           ...
       username=DESIRED_USERNAME
           ...
    """
    configs = get_cab_configs()
    if 'username' in configs['DB']:
        return configs['DB']['username']
    else:
        return DEFAULT_MONGODB_USER


def get_db_connection():
    """get DB connection.  
       user-level config file must exist (see above) and have a 
       section with the form:

       [DB]
       username=[...]
       password=[...]  
    """
    configs = get_cab_configs()
    user = get_db_user()
    pwd = configs['DB']['password']
    host = get_db_host()
    port = get_db_port()
    connstr = "mongodb://%s:%s@%s:%s" % (user, pwd, host, port)
    try:
        conn = pm.MongoClient(connstr)
    except:
        print('Could not connect to database. Have you set up your SSH tunnel?')
        sys.exit()
    return conn

