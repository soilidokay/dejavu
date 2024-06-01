# load config from a JSON file (or anything outputting a python dictionary)
import os
import sys
sys.path.append('.')
from dejavu import Dejavu

config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password",
        "database": "dejavu"
    },
    "database_type": "postgres"
}

data_dir = 'app/data'

if __name__ == '__main__':
    djv = Dejavu(config)
    djv.fingerprint_directory(data_dir, [".wav", ".mp3"])
