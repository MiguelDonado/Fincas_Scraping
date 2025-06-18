from pathlib import Path

BASE_REF_CATASTRAL_URL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del={provincia}&mun={municipio}&RefC={ref_catastral}"
BASE_URL_SEARCH_CATASTRO = (
    "https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?buscar=S"
)
BASE_URL_REPORT_CATASTRO = "https://www1.sedecatastro.gob.es/Accesos/SECAccvr.aspx"
DOWNLOAD_DIR = Path("../data/catastro").resolve()
DOWNLOAD_DIR_REPORT = Path("../data/report").resolve()
EMPTY_DICTIONARY = {
    "ath": None,
    "denominacion_ath": None,
    "agrupacion_cultivo": None,
    "agrupacion_municipio": None,
    "number_buildings": None,
    "slope": None,
    "fls": None,
}
BASE_URL_OTROS_VISORES_GENERAL = (
    "https://www1.sedecatastro.gob.es/Cartografia/BuscarParcelaInternet.aspx?refcat="
)
