from pathlib import Path

import regex

ELECTRONIC_CSV_PATTERN = regex.compile(r"se\.bog\.adneicah.*:VSC", flags=regex.DOTALL)

DOWNLOAD_DIR = Path("../data/auction").resolve()

# Number of delegations are 57 in total
NUMBER_OF_DELEGATIONS = (
    57  # This number is for testing purposes, so it only run on a few provinces.
)

DELEGATIONS = range(1, NUMBER_OF_DELEGATIONS)

BASE_URL_HACIENDA = "https://www.hacienda.gob.es"
DELEGATION_URL = (
    "https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Patrimonio%20del%20Estado/"
    "Gestion%20Patrimonial%20del%20Estado/Paginas/Subastas/ListadoSubastasConcursos.aspx?"
    "den=&nat=&dels={code}%3B"
)
PLIEGO_PATTERN = regex.compile(".*liego.*", flags=regex.IGNORECASE)
ANEXO_PATTERN = regex.compile(".*nexo.*", flags=regex.IGNORECASE)

###################################### REGEX PROCESS PLIEGO PDF ##############################################################
COMMON_REGEX = (
    r"(?<!.*(?:sur|norte|registr|situad|calle|rústica|urbana|oeste|este|folio|linderos|c.digo|Propiedad Horizontal|(?:con|,|la) finca).*\n?.*)"
    r"(?:LOTE|BIEN|FINCA)\s(?!registral)(?:Nº)?\D{0,10}?\d{1,3}\D(?!%)(?!.*(?:Propiedad\sHorizontal|escalera))"
)

AUCTION_HREF_PATTERN = regex.compile("^https://.+Estado/Paginas/Subastas/.+")
# The first segment of the regex is for "fincas rusticas", the second for "fincas urbanas", the third is for a strange case
REF_CATASTRAL_PATTERN = regex.compile(
    r"^"
    r"(?<!.*(?:sur|norte|oeste|este|calle).*\n?.*)"
    r".*Referen\s?cias?\s+"
    r"(?:Catastral)?"
    r"(?:es)?"
    r"(?:\sde\sla\sfinca\srústica)?"
    r"(?:\ses\sla)?:?\s*"
    r"("
    r"\d{2}\d{3}[A-Z]\d{3}\d{5}\d{4}[A-Z]{2}|"
    r"\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2}|"
    r"\d{7}[A-Z]{2}\d{4}[A-Z]"
    r")",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

# Checkers to know the type of pdf we are analyzing
CHECKER_SECOND_STRUCTURE_PATTERN = regex.compile(
    COMMON_REGEX, flags=regex.MULTILINE | regex.IGNORECASE
)

CHECKER_GARANTIA_IN_PARAGRAPH_PATTERN = regex.compile(
    r"^.*(garant.a|fianza)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

CHECKER_SECOND_STRUCTURE_PRICE_IN_TABLE_FORMAT = regex.compile(
    r"^(Subasta\sPrimera\sSegunda\sTercera\sCuarta|SUBASTA 1ª 2ª 3ª 4ª)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

CHECKER_SECOND_STRUCTURE_PRICE_IN_THE_PARAGRAPH = regex.compile(
    r"\d+[\d\.]*(,\d\d|\seuro)"
)

# This is the regular expression that is able to handle the pliego pdf that has the next structure (tables)
# Example: https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH%20OURENSE/Pliego_Sub.30_abril_2024.pdf
FIRST_PARAGRAPHS_PATTERN = regex.compile(
    r"^(?:Rústica|Urbana).*?Referencia\sCatastral:[\w ]+$",
    flags=regex.DOTALL | regex.MULTILINE,
)
PRICE_FIRST_STRUCTURE_PDF_PATTERN = regex.compile(r"(?<=\s)[\d\.,]+\s€")
# This is the regular expression that is able to handle the pliego pdf that has the next structure (paragraphs)
# Example: https://www.hacienda.gob.es/DGPatrimonio/Gesti%C3%B3n%20Patrimonial/subastas/DEH_TERUEL/Pliego%20de%20condiciones%20subasta.pdf
SECOND_PARAGRAPHS_PATTERN = regex.compile(
    (
        COMMON_REGEX
        + r"(?:.|\n){30,}?"  # This is all that is in the middle of the paragraph
        + rf"(?={COMMON_REGEX}|^Segunda[:\.]\s)"
    ),
    flags=regex.MULTILINE | regex.IGNORECASE,
)
###### (On the second pdf structure). If have "garantia" on the paragraph:
PRICE_SECOND_STRUCTURE_PDF_WITH_GARANTIA_PATTERN = regex.compile(
    (
        r"^"
        r".*(?:licitaci.n|salida).*?"
        r"(?:(\d+[\d\.,]*)\s*?(?:euros|€|\d)|\n(?!.*tasación).*?(\d+[\d\.,]*)\s*?(?:euros|€))"
    ),
    flags=regex.MULTILINE | regex.IGNORECASE,
)

###### (On the second pdf structure). If have "garantia" on the paragraph and the price is on table format:
PRICE_SECOND_STRUCTURE_PDF_WITH_GARANTIA_PATTERN_AND_TABLE_FORMAT = regex.compile(
    r"^.*(?:licitaci.n)\s+.*?(\d+[\d\.,]*)\s",
    flags=regex.MULTILINE | regex.IGNORECASE,
)


###### (On the second pdf structure). If doesn't have "garantia" on the paragraph:
PRICE_SECOND_STRUCTURE_PDF_WITHOUT_GARANTIA_PATTERN = regex.compile(
    r"^.*(?:subasta|precio|precio\sde\ssalida).{0,10}?(\d+[\d\.,]*)\s+(?:Euros|€)",
    flags=regex.MULTILINE | regex.IGNORECASE,
)

#### (On the second pdf structure). If price is not included on the paragraph but at the end of the file.
PRICE_WHEN_IS_NOT_IN_PARAGRAPH = regex.compile(
    r"^\d+\s.*subasta.*?(\d+[\d\.,]*\d)", flags=regex.MULTILINE | regex.IGNORECASE
)

# https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=90&RefC=15090A507018480000AY
