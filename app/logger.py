import logging
import os

level = logging.DEBUG if os.getenv("DEBUG") == 'True' else logging.INFO
logging.basicConfig(level=level)

logger = logging.getLogger("app")