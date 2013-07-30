import default_logger as logger

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
