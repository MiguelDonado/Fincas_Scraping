# Create a custom logger and set it up. To use this logger, we'll import this file
# Doing this'll set up the configuration on the other file.
# It also contains a function used to build an id, that will be at the beggining
# of the log message.

import datetime as dt
import logging
from pathlib import Path

today = dt.datetime.today()
debug_filename = Path(
    f"logs/debug_{today:%y}{today.month:02d}{today.day:02d}.log"
).resolve()

error_filename = Path(
    f"logs/error_{today:%y}{today.month:02d}{today.day:02d}.log"
).resolve()

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the root logger level to INFO

# Create handlers
debug_handler = logging.FileHandler(debug_filename)  # Save on a file
debug_handler.setLevel(logging.DEBUG)

error_handler = logging.FileHandler(error_filename)  # Save on a file
error_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler()  # Print to console

# Create formatters and add them to the handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)-8s -> %(message)s")
debug_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(debug_handler)
logger.addHandler(error_handler)
logger.addHandler(stream_handler)


# Build an id to know which delegation, lote and land is being processed.
def build_id(delegation: int, lote: int = ".", land: int = "."):

    # Validate the data types of our arguments
    assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
    assert (
        lote == "." or lote > 0
    ), f"Lote {lote} is not greater than zero neither empty!"
    assert (
        land == "." or land > 0
    ), f"Land {land} is not greater than zero neither empty!"

    s_delegation = str(delegation)
    s_lote = str(lote)
    s_land = str(land)
    return f"{s_delegation:^4}- {s_lote:^4}- {s_land:^4} - "
