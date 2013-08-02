# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

"""
Remarks:
Defines the default logger.

Any logger the following symbols:

TRACE = 10
DEBUG = 20
INFO  = 30
WARN  = 40
ERROR = 50

setLevel(level)
trace(msg, *args)
debug(msg, *args)
info(msg, *args)
warn(msg, *args)
error(msg, *args)
"""

TRACE = 10
DEBUG = 20
INFO = 30
WARN = 40
ERROR = 50

_LEVEL = TRACE


def setLevel(level):
    global _LEVEL
    _LEVEL = level


def trace(msg, *args):
    global _LEVEL
    global TRACE
    if _LEVEL <= TRACE:
        print ("TRACE: " + msg) % args


def debug(msg, *args):
    global _LEVEL
    global DEBUG
    if _LEVEL <= DEBUG:
        print ("DEBUG: " + msg) % args


def info(msg, *args):
    global _LEVEL
    global INFO
    if _LEVEL <= INFO:
        print ("INFO: " + msg) % args


def warn(msg, *args):
    global _LEVEL
    global WARN
    if _LEVEL <= WARN:
        print ("WARN: " + msg) % args


def error(msg, *args):
    global _LEVEL
    global ERROR
    if _LEVEL <= ERROR:
        print ("ERROR: " + msg) % args
