# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger('ton_client.tonlib')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
h = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
h.setFormatter(formatter)

logger.addHandler(h)
