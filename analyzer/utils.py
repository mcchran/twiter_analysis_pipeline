import csv
import os
import json
import keras
import yaml
import logging
from functools import partial


CONFIG_FILE_PATH = "../config.yml"

COMMA = ","
EMPTY_STRING = ""
QUOTES_MARK= '"'


def append_to_csv(entry, file_path, delimeter=None,
                  newline=None, quotechar=None, log=None):
    """ Utility function to append multiple rows (batch) into a csv file

    :param list: list of lists of the lines to append
                    e.g. [[value 1, value2], .... ]
    :param str file_path: the path of the csv file to append the rows to
                            if it does not exist the file is created
    :param str delimeter: value delimeter, defaults to comma
    :param str newline: the line delimeter defaults to empty string
    :param str quotechar: the quotetion mark, defaults to | symbol
    :param function log: boolean to enable logging info
    """
    delimeter = delimeter or COMMA
    newline = newline or EMPTY_STRING
    quotechar = quotechar or QUOTES_MARK
    log = log or False

    with open(file_path, 'a', newline='') as csvfile:
        try:
            # add the date to the first
            writer = csv.writer(
                                    csvfile, delimiter=delimeter,
                                    quotechar=quotechar,
                                    quoting=csv.QUOTE_MINIMAL)
            writer.writerow(entry)
            if log:
                logging.info(f"Upcoming CSV entry {entry}")
        except Exception as e:
            logging.exception(f"Writing to csv failed with {e}")
            raise e


def get_absolute_path(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)


def load_yaml_config():
    config_path = get_absolute_path(CONFIG_FILE_PATH)
    with open(config_path, 'r') as f:
        return yaml.full_load(f)


def load_json_file(relative_path):
    absolute_path = get_absolute_path(relative_path)
    with open(absolute_path) as schema_file:
        return json.loads(schema_file.read())


def load_model(relative_path):
    absolute_path = get_absolute_path(relative_path)
    return keras.models.load_model(absolute_path)


def config_setup(section=None):
    """ That is a convenient decorator function to provide an lean
    pipeline customization. It actually connect all decorated function with
    the yaml file defintions. No need to move arguments around.

    :param string section: valid section key.
    """
    if section:
        yaml_kwargs = load_yaml_config()['func'][section]
    else:
        yaml_kwargs = {}
    print(yaml_kwargs)

    def decorated(func):
        def wrapped(*fargs, **fkwargs):
            return func(*fargs, **fkwargs, **yaml_kwargs)
        return wrapped
    return decorated

class ChainExcpetion(Exception):
    pass


class Chain():

    def __init__(self, logging_at_level=None):
        """ Convolutes functions
        Developer is responsible for maintaining actions to be compatible

        :param func logging_at_level: optional function to log in case
                                      of failure
        """
        self.actions = []
        self.state = None
        self.logging_at_level = logging_at_level

    def append(self, function):
        """ Appends a new function to the action execution pipeline.

        :param func function: the function to append to the chain
        """
        self.actions.append(function)
        return self

    def run(self, arg_list):
        self.state = arg_list
        for action in self.actions:
            try:
                self.state = action(self.state)
            except Exception as e:
                if self.logging_at_level:
                    self.logging_at_level(ChainExcpetion(e))
                raise ChainExcpetion(e)

        return self.state
