from pygelf import GelfUdpHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(GelfUdpHandler(host='178.128.165.188', port=12201))

logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
logger.info('Hello, GELF!')
