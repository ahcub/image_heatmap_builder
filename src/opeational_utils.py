import logging
import os
import sys
from os import getcwd
from os.path import join, isdir

LOGGING_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
DATE_FORMAT = '[%Y-%m-%d %H:%M:%S]'

logging.getLogger().level = logging.DEBUG


def configure_stream_logger(stream=sys.stdout, level='DEBUG'):
    stream_handler = logging.StreamHandler(stream=stream)
    stream_handler.level = logging.getLevelName(level)
    formatter = logging.Formatter(datefmt=DATE_FORMAT, fmt=LOGGING_FORMAT)
    stream_handler.setFormatter(formatter)
    logging.getLogger().addHandler(stream_handler)


def configure_file_logger(filename='app.log', level='DEBUG'):
    file_handler = logging.FileHandler(filename=join(getcwd(), filename))
    file_handler.level = logging.getLevelName(level)
    formatter = logging.Formatter(datefmt=DATE_FORMAT, fmt=LOGGING_FORMAT)
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)


def configure_file_and_stream_logger(stream=sys.stdout, filename='app.log', level='DEBUG'):
    configure_stream_logger(stream, level)
    configure_file_logger(filename, level)


def mkpath(path):
    if not isdir(path):
        os.makedirs(path)
