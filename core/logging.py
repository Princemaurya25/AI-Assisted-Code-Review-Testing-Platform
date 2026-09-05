import logging
import sys


def setup_logging():
    logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=logging_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence noisy loggers if necessary
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("code_review_platform")
