# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import unittest

from hsm import default_logger as logger

class TestLogger(unittest.TestCase):

    def test_logger(self):
        logger.trace("hello %s" % ("world",))
        logger.debug("hello %s" % ("world",))
        logger.info("hello %s" % ("world",))
        logger.error("hello %s" % ("world",))
        logger.warn("hello %s" % ("world",))
        logger.setLevel(logger.INFO)

        print "LEVEL = INFO"

        logger.trace("hello %s" % ("world",))
        logger.debug("hello %s" % ("world",))
        logger.info("hello %s" % ("world",))
        logger.warn("hello %s" % ("world",))
        logger.error("hello %s" % ("world",))
