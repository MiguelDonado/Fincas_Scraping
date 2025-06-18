from pathlib import Path

import regex

BASE_URL = "https://www.google.com/maps"
DOWNLOAD_DIR = Path("../data/googlemaps").resolve()
KM_PATTERN = regex.compile(r"\s.*")
