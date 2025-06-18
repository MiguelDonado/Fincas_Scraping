# URLS

### Catastro
BASE_REF_CATASTRAL_URL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?del=15&mun=12&UrbRus=R&RefC=15012B514003380000LQ&Apenom=&esBice=&RCBice1=&RCBice2=&DenoBice=&from=nuevoVisor&ZV=NO&anyoZV="
BASE_URL_SEARCH_CATASTRO = (
    "https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?buscar=S"
)
BASE_URL_REPORT_CATASTRO = "https://www1.sedecatastro.gob.es/Accesos/SECAccvr.aspx"

### Correos
BASE_URL_CORREOS = "https://www.correos.es/es/es/herramientas/codigos-postales/detalle"

### GoogleMaps
BASE_URL_GOOGLE_MAPS = "https://www.google.com/maps"

### Hacienda
BASE_URL_HACIENDA = "https://www.hacienda.gob.es"
DELEGATION_URL = (
    "https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Patrimonio%20del%20Estado/"
    "Gestion%20Patrimonial%20del%20Estado/Paginas/Subastas/ListadoSubastasConcursos.aspx?"
    "den=&nat=&dels=15%3B"
)

### Iberpix
BASE_URL_IBERPIX = "https://www.ign.es/iberpix/"

### INE
BASE_URL_INE = "https://www.ine.es/jaxiT3/Tabla.htm?t=6152"
POBLACION_URL_INE = "https://www.ine.es/nomen2/index.do"


# Test data
data_test = {
    "delegation": 10,
    "i_lote": 2,
    "i_land": 1,
    "land": "15012B514003380000LQ",
    "coordinates_land": """39°28'23.6"N 6°23'41.4"W""",
    "localizacion": "CL VIVIENDAS DE CAMINEROS Ndup-U Bl:21 Es:1 Pl:02 Pt:DCH 10005 CACERES (CÁCERES)",
    "enterprise_direction": "39.49005, -6.41633",
    "enterprise_nombre": "Catelsa Caceres SA",
    "clase": "Rústico",
    "cp": "10005",
    "locality": "CACERES",
    "path_kml_land": "/home/miguel/CodingProjects/HaciendaFincas_Scraping/data/catastro/15012B514003380000LQ.kml",
}
