import logging
from time import sleep

import seqlog

server_url = "http://178.128.165.188:5341/"
api_key = ""

log_handler = seqlog.log_to_seq(
    server_url,
    api_key,
    level=logging.INFO,
    auto_flush_timeout=0.2,
    additional_handlers=[logging.StreamHandler()],
    override_root_logger=True
)

print("Running...")

logging.info("Hi, {name}. {greeting}", name="Root logger", greeting="Nice to meet you")

sleep(1)


