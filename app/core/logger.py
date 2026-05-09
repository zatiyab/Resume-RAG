import logging
import sys

def setup_logger(name="hiremind"):
    """
    Sets up and returns a configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, it's already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Create console handler and set level to INFO
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)

    return logger

# Create a default logger instance to be imported by other modules
logger = setup_logger()
