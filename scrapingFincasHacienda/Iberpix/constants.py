from pathlib import Path

BASE_URL_IBERPIX = "https://iberpix.cnig.es/iberpix/visor"
DOWNLOAD_DIR = Path("../data/iberpix").resolve()
SUFFIX_FILENAME_CURVAS_NIVEL = "_mapa_curvas_nivel.png"
SUFFIX_FILENAME_LIDAR = "_mapa_lidar.png"
SUFFIX_FILENAME_USOS_SUELO = "_mapa_usos_suelo.png"
SUFFIX_FILENAME_HIDROGRAFIA = "_mapa_hidrografia.png"

##### LAYERS ######
HIDROGRAFIA = "https://servicios.idee.es/wms-inspire/hidrografia?"
ORTOFOTOS_PROVISIONALES = "https://wms-pnoa.idee.es/pnoa-provisionales?"

EMPTY_DICTIONARY_PATHS = {
    "curvas_nivel": None,
    "lidar": None,
    "usos_suelo": None,
    "ortofoto_hidrografia": None,
}
EMPTY_DICTIONARY_DATA = {
    "ID": None,
    "Código iberpix": None,
    "Cubierta terrestre iberpix": None,
    "Código CODIIGE": None,
    "Cubierta terrestre CODIIGE": None,
    "Código Uso de suelo": None,
    "Uso del suelo HILUCS": None,
    "Superficie (Ha)": None,
}
EMPTY_DICTIONARY = {"data": EMPTY_DICTIONARY_DATA, "paths": EMPTY_DICTIONARY_PATHS}
