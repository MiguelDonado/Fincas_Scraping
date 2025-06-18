# Function used to extract the "newest" auction url of a delegation.

import requests
import regex
import logging
from bs4 import BeautifulSoup

import logger_config
import Hacienda.constants as const
from typing import Union


# A delegation could've more than one auction anchor:
#      Reason Nº1) The 2nd, 3rd round for the same auction.
#      Reason Nº2) Another auction.

# |SOLUTION|
#   o Select the first element of the array (this way I'm selecting the newest url)
#     Since the data would be stored on a database, it doesn't matter if we don't retrieved
#     the older anchors, because they would be already on the database.
#     (the script'll be run daily)

#   - Downside -
#       When it's run for the first time the database is empty, so if there's more than one anchor
#       we'd be losing the information of the oldest links.


# Logger configuration
logger = logging.getLogger(__name__)


def has_auction(delegation: int) -> Union[str, None]:

    # Validate the data types of our arguments
    assert delegation > 0, f"Delegation {delegation} is not greater than zero!"

    delegation_url = const.DELEGATION_URL.format(code=delegation)
    html_text = requests.get(delegation_url)
    soup = BeautifulSoup(html_text.text, "lxml")
    # Using the walrus operator. Initializes the variable, and checks if it's True
    if auction_anchor := soup.find("a", href=const.AUCTION_HREF_PATTERN):
        auction_href = auction_anchor.get("href")

        # Log
        msg = f"Auction retrieved: {auction_href}"
        logger.info(f"{logger_config.build_id(delegation)}{msg}")

        return auction_href
    else:

        # Log
        msg = "No auctions available"
        logger.info(f"{logger_config.build_id(delegation)}{msg}")

        return None
