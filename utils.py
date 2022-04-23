import sys
import os
import configparser
import pymongo as pm

from settings import (DEFAULT_CONFIG_FILENAME,
                      DEFAULT_MONGODB_PORT,
                      DEFAULT_MONGODB_HOST)

if "CAB_CONFIGFILE" in os.environ:
    CONFIGFILE = os.environ["CAB_CONFIGFILE"]
else:
    CONFIGFILE = os.path.join(os.environ["HOME"],
                              DEFAULT_CONFIG_FILENAME)

_cab_configs = None
def get_cab_configs():
    global _cab_configs
    if _cab_configs is None:
        config = configparser.ConfigParser()
        config.read(CONFIGFILE)
        _cab_configs = config
    return _cab_configs


def get_db_port():
    configs = get_cab_configs()
    if 'port' in configs['DB']:
        return configs['DB']['port']
    else:
        return DEFAULT_MONGODB_PORT


def get_db_host():
    configs = get_cab_configs()
    if 'host' in configs['DB']:
        return configs['DB']['host']
    else:
        return DEFAULT_MONGODB_HOST
    

def get_db_connection():
    configs = get_cab_configs()
    user = configs['DB']['username']
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

