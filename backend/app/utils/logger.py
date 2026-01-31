import logging
from app.core.config import LOG_LEVEL

def configure_logging():
    """ Configure root logger to log to console with level from config.
    """
    root = logging.getLogger()

    # Remove existing file handlers (if any) so logs do NOT go to disk.
    root.handlers = [h for h in root.handlers if not isinstance(h, logging.FileHandler)]

    # Set level from config
    root.setLevel(LOG_LEVEL)

    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    # Add a StreamHandler if there isn't one already
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        root.addHandler(sh)

# Run configure immediately on import so other modules get logging ready
configure_logging()
logger = logging.getLogger(__name__)
