import logging
import os
import sys

LOG_FILE = os.environ.get("LOGFILE", "default_logfile.log")


def _init_logger():
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        return logger
    except Exception as e:
        print(f"Error initializing logger: {e}", file=sys.stderr)
        raise


try:
    log = _init_logger()
except Exception:
    # Fallback to basic logging if initialization fails
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
    log = logging.getLogger(__name__)
    log.error("Failed to initialize custom logger. Using basic configuration.")
