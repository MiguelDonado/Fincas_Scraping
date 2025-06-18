# Contains several functions, that are all used when calling the function get_pliego_info. Given the PDF that contains the list of lands in auction, it extracts
# the ref_catastral and the price

import io
import logging
from typing import Union

import Hacienda.constants as const
import logger_config
import pdfplumber
import regex
import requests
from bs4 import BeautifulSoup

# Logger configuration
logger = logging.getLogger(__name__)


def get_auction_id(url_pdf, delegation, auction):
    try:
        id = get_csv(url_pdf)
        # If the PDF doesnt have a csv, then generate an id mixing the url and the celebration date
        if not id:
            id = generate_unique_id(url_pdf, auction)
        return id
    except Exception as e:

        # Log
        msg = "Failed to get a unique identifier for the auction using get_auction_id function {e}"
        logger.error(f"{logger_config.build_id(delegation)}{msg}", exc_info=True)
        return None


def generate_unique_id(url_pdf, auction):
    html_text = requests.get(auction)
    soup = BeautifulSoup(html_text.text, "lxml")
    celebration_date_div = soup.find("div", id=lambda x: x and "FechaCelebracion" in x)
    if celebration_date_div:
        celebration_date = celebration_date_div.text.strip().replace(" ", "")
        id = f"{url_pdf}___date_{celebration_date}"
        return id


def get_csv(url_pdf):
    text = read_pdf(url_pdf, only_first_page=True)
    subset_csv = regex.search(const.ELECTRONIC_CSV_PATTERN, text).group()
    # f stands for formatted
    f_subset_csv = regex.sub(r"\n+", " ", subset_csv)
    list_subset_csv = regex.split(" ", f_subset_csv)
    reverse_csv = list_subset_csv[-2]
    csv = reverse_csv[::-1]
    return csv


def get_lotes_data(url_pdf: str, delegation: int) -> dict[str, Union[int, dict]]:

    # Validate the data types of our arguments
    assert isinstance(url_pdf, str), f"Url_pdf {url_pdf} must be a string!"
    assert delegation > 0, f"Delegation {delegation} is not greater than zero!"

    try:
        text = read_pdf(url_pdf)
        lotes = get_lotes(text)

        #   The variable lotes_data is a list of dictionaries:
        #   [ {"refs": [ref1, ref2], "price": price}, {"refs": [ref1], "price": price} ]
        #      ____________________________________
        #     |               LOTE 1               |
        if lotes["structure"] == "tables":
            lotes_data = [
                get_desired_information("tables", lote) for lote in lotes["text"]
            ]

        elif lotes["structure"] == "paragraphs":
            lotes_data = [
                get_desired_information("paragraphs", lote) for lote in lotes["text"]
            ]

        # The variable 'lotes' contains all the text for each lote
        # The variable 'lotes_data' contains the desired data for each lote   {refs, price}

        # Price = None (some error happened)
        # Price = -1 (prices are not included on the same paragraph, but all together at the end)

        first_lote_price = lotes_data[0]["price"]
        if first_lote_price == -1:
            prices = regex.findall(const.PRICE_WHEN_IS_NOT_IN_PARAGRAPH, text)
            prices = [format_price(price) for price in prices]

            for lote_data, price in zip(lotes_data, prices):
                lote_data["price"] = price

        for lote_num, lote_data in enumerate(lotes_data, 1):
            # When the processing of a lote gives some error, it returns (None, None)
            if lote_data["refs"] == None:

                # Log
                msg = f"Failed to process the lote {lote_num}"
                logger.warning(f"{logger_config.build_id(delegation, lote_num)}{msg}")

            else:

                # Log
                msg = f"{lote_data['refs']}, {lote_data['price']}"
                logger.info(f"{logger_config.build_id(delegation, lote_num)}{msg}")

        # The variable lotes_data is a list of dictionaries with two keys.
        #   1) Id: A number
        #   2) Data: A dictionary with two keys {refs, price}
        #   lotes_data = [{id, {refs, price}},{id, {refs, price}}]
        lotes_data = [
            {"id": i, "data": lote}
            for i, lote in enumerate(lotes_data, 1)
            if lote_data["refs"]
        ]

        return lotes_data
    except Exception as e:

        # Log
        msg = "Failed to proccess auction PDF using get_lotes_data function {e}"
        logger.error(f"{logger_config.build_id(delegation)}{msg}", exc_info=True)

        return None


# Given a url of a PDF, it returns the text in one string
def read_pdf(url_pdf: str, only_first_page=False) -> str:

    # Validate the data types of our arguments
    assert isinstance(url_pdf, str), f"Url_pdf {url_pdf} must be a string!"

    response = requests.get(url_pdf)
    pdf_binary = response.content
    pdf_content = io.BytesIO(pdf_binary)
    with pdfplumber.open(pdf_content) as pdf:
        # Extract content from all the pages, to parse lotes...
        if not only_first_page:
            text_pages = [page.extract_text() for page in pdf.pages]
            text = " ".join(text_pages)
        # Extract only the first page (to get the electronic csv)
        else:
            text = pdf.pages[0].extract_text()
    return text


# Given a text, it returns a dictionary with two keys.
#   1) Type of structure
#   2) List:
#       o Each element represents all the text of a lote
def get_lotes(text: str) -> dict[str, Union[str, list[str]]]:

    # Validate the data types of our arguments
    assert isinstance(text, str), f"Text {text} must be a string!"

    if regex.search(const.CHECKER_SECOND_STRUCTURE_PATTERN, text):
        structure = "paragraphs"
        lotes = regex.findall(const.SECOND_PARAGRAPHS_PATTERN, text)
    else:
        structure = "tables"
        lotes = regex.findall(const.FIRST_PARAGRAPHS_PATTERN, text)
    return {
        "structure": structure,
        "text": lotes,
    }


# Given the structure of the lote text, and the lote itself
# It returns a dictionary with two keys.
#   1) List of referencias catastrales
#   2) Price
def get_desired_information(
    structure: str, lote: str
) -> dict[str, Union[list[str], float]]:

    # Validate the data types of our arguments
    assert isinstance(structure, str), f"Structure {structure} must be a string!"
    assert isinstance(lote, str), f"Lote {lote} must be a string!"

    try:
        refs = get_ref_catastral(lote)
        price = get_precio(structure, lote)
        return {"refs": refs, "price": price}
    except AttributeError:
        return {"refs": None, "price": None}


# Given a lote it extracts the referencias catastrales of the lands that integrate it.
# It returns a list of refs.
def get_ref_catastral(lote: str) -> list[str]:

    # Validate the data types of our arguments
    assert isinstance(lote, str), f"Lote {lote} must be a string!"

    ref_catastrales = regex.findall(const.REF_CATASTRAL_PATTERN, lote)
    if len(ref_catastrales) >= 1:
        return ref_catastrales
    else:
        raise AttributeError("There is not a valid referencia catastral")


# Given the structure of the lote, and the text on it,
# it returns the price
def get_precio(structure: str, lote: str) -> float:

    # Validate the data types of our arguments
    assert isinstance(structure, str), f"Structure {structure} must be a string!"
    assert isinstance(lote, str), f"Lote {lote} must be a string!"

    if structure == "tables":
        price = regex.search(const.PRICE_FIRST_STRUCTURE_PDF_PATTERN, lote)
        return format_price(price.group())  # Returns the whole match

    elif structure == "paragraphs":
        # If the price is not included on the lote
        if not has_price(lote):
            return -1
        if regex.search(const.CHECKER_GARANTIA_IN_PARAGRAPH_PATTERN, lote):
            if regex.search(const.CHECKER_SECOND_STRUCTURE_PRICE_IN_TABLE_FORMAT, lote):
                price = regex.search(
                    const.PRICE_SECOND_STRUCTURE_PDF_WITH_GARANTIA_PATTERN_AND_TABLE_FORMAT,
                    lote,
                )
                return format_price(price.group(1))
            else:
                price = regex.search(
                    const.PRICE_SECOND_STRUCTURE_PDF_WITH_GARANTIA_PATTERN, lote
                )
                final_price = price.group(1) or price.group(2)
                return format_price(final_price)
        else:
            price = regex.search(
                const.PRICE_SECOND_STRUCTURE_PDF_WITHOUT_GARANTIA_PATTERN, lote
            )
            return format_price(price.group(1))


def format_price(price: str) -> float:

    # Validate the data types of our arguments
    assert isinstance(price, str), f"Price {price} must be a string!"

    return float(
        price.replace(".", "").replace(",", ".").replace(" ", "").replace("€", "")
    )


# Given the text of a lote, it checks if it contains the price
def has_price(lote: str):

    # Validate the data types of our arguments
    assert isinstance(lote, str), f"Lote {lote} must be a string!"

    result = regex.search(const.CHECKER_SECOND_STRUCTURE_PRICE_IN_THE_PARAGRAPH, lote)
    return result
