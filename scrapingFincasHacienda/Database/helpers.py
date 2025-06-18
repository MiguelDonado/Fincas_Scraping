import logging
import sqlite3
from pathlib import Path

import Database.constants as const
import logger_config
import regex
from Database.models import (
    AgrupacionCultivo,
    Aprovechamiento,
    Auction,
    BaseDatabase,
    Clase,
    CodigoPostal,
    CubiertaTerrestreCodigee,
    CubiertaTerrestreIberpix,
    Delegation,
    Empresa,
    EmpresaFinca,
    Finca,
    Locality,
    Lote,
    Municipio,
    Province,
    Territorio,
    Uso,
    UsosSueloHilucs,
)

logger = logging.getLogger(__name__)


# Check if the land, it's stored on database.
# If so, auction is skipped, because its not new, its the second... round of an existing auction.
# Otherwise the auction is new."""
# Returns Truthy value if its old, Falsy value if its new
def is_auction_old_or_posterior_rounds(delegation, referencia_catastral):
    db_path = Path(const.DB_NAME)
    is_created_db = db_path.exists()
    if is_created_db:
        db = BaseDatabase()
        finca = Finca()
        finca_id = finca.get_finca_id(referencia_catastral)
        db.close_connection()

        if finca_id:
            # Log
            msg = f"Auction that contains land '{referencia_catastral}' has already been processed. Skipping to the next auction..."
            logger.info(f"{logger_config.build_id(delegation)}{msg}")
            return finca_id
        else:
            # Log
            msg = f"Corroborated that auction is NEW."
            logger.info(f"{logger_config.build_id(delegation)}{msg}")
            return finca_id
    else:
        # Log
        msg = f"Corroborated that auction is NEW."
        logger.info(f"{logger_config.build_id(delegation)}{msg}")
        return None


# Returns Truthy value if its old, Falsy value if its new
def is_auction_id_old(delegation, id_auction):
    db_path = Path(const.DB_NAME)
    is_created_db = db_path.exists()
    if is_created_db:
        db = BaseDatabase()
        auction = Auction()
        result = auction.get_auction_id(electronical_id=id_auction)
        db.close_connection()

        if result:
            # Log
            msg = f"Auction with id '{id_auction}' is already stored on database. Skipping this auction and continuing with next delegation..."
            logger.info(f"{logger_config.build_id(delegation)}{msg}")
        else:
            # Log
            msg = f"Auction with id '{id_auction}' is NEW."
            logger.info(f"{logger_config.build_id(delegation)}{msg}")
        return result
    else:
        # Log
        msg = f"Auction with id '{id_auction}' is NEW."
        logger.info(f"{logger_config.build_id(delegation)}{msg}")
        return None


# Returns Truthy value if its old, Falsy value if its new
# Involved table: 'Locality'
def is_ine_population_in_db(delegation, lote, land, ref, locality, municipio):
    db_path = Path(const.DB_NAME)
    is_created_db = db_path.exists()
    if is_created_db:
        db = BaseDatabase()
        locality = Locality(locality, municipio)
        result = locality.get_locality_id()
        db.close_connection()

        if result:
            # Log
            msg = f"Locality '{locality}' from municipio '{municipio}' is already stored on database. Skipping INE population scraping process."
            logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        else:
            # Log
            msg = f"Locality '{locality}' from municipio '{municipio} is NEW."
            logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        return result
    else:
        # Log
        msg = f"Locality '{locality}' from municipio '{municipio} is NEW."
        logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        return None


# Returns Truthy value if its old, Falsy value if its new
# Involved table: 'Province'
def is_ine_transmisiones_rust_in_db(delegation, lote, land, ref, cp):
    db_path = Path(const.DB_NAME)
    is_created_db = db_path.exists()
    if is_created_db:
        db = BaseDatabase()
        province = Province(cp[0:2])
        result = province.get_province_id()
        db.close_connection()

        if result:
            # Log
            msg = f"Province '{cp[0:2]}' is already stored on database. Skipping 'province transmisiones fincas rusticas' process."
            logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        else:
            # Log
            msg = f"Province '{cp[0:2]}' is NEW."
            logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        return result
    else:
        # Log
        msg = f"Province '{cp[0:2]}' is NEW."
        logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        return None


# Returns Truthy value if its old, Falsy value if its new
# Involved table: 'CodigoPostal'
def is_sabi_in_db(delegation, lote, land, ref, cp):
    db_path = Path(const.DB_NAME)
    is_created_db = db_path.exists()
    if is_created_db:
        db = BaseDatabase()
        codigo_postal = CodigoPostal(cp)
        result = codigo_postal.get_codigo_postal_id()
        db.close_connection()

        if result:
            # Log
            msg = f"Codigo postal '{cp}' is already stored on database. Skipping 'sa_-_bi' process."
            logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        else:
            # Log
            msg = f"Codigo postal '{cp}' is NEW."
            logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        return result
    else:
        # Log
        msg = f"Codigo postal '{cp}' is NEW."
        logger.info(f"{logger_config.build_id(delegation, lote, land)}{msg}")
        return None


def insert_land_data(land_data, mode="BASIC"):

    ###### 1. INSTANTIATION OF OBJECTS ######
    db = BaseDatabase()
    clase = Clase()
    uso = Uso()
    agrupacion_cultivo = AgrupacionCultivo()
    aprovechamiento = Aprovechamiento()
    province = Province()
    municipio = Municipio()
    locality = Locality()
    codigo_postal = CodigoPostal()
    delegation = Delegation()
    auction = Auction()
    territorio = Territorio()
    lote = Lote()
    empresa = Empresa()
    finca = Finca()
    cubierta_terrestre_iberpix = CubiertaTerrestreIberpix()
    cubierta_terrestre_codigee = CubiertaTerrestreCodigee()
    usos_suelo_hilucs = UsosSueloHilucs()
    empresa_finca = EmpresaFinca()

    ###### 2. INSERTION OF DATA ######
    #       -> On the insert methods of each table (class) two things are already handled
    #           a) Check if the data to be inserted != None.
    #           b) Check if the data to be inserted is already on the table (then do nothing)
    # 2.1. Table 'clases' is already created and populated.
    # 2.2. Table 'usos' is already created and populated.
    # 2.3. Table 'agrupacion_cultivos'
    agrupacion_cultivo.insert_data(land_data["agrupacion_cultivo"])
    # 2.4. Table 'aprovechamientos'
    aprovechamiento.insert_data(land_data["aprovechamiento"])
    # 2.5. Table 'provinces'
    province.insert_data(
        land_data["province"],
        land_data["rusticas_transactions_now"],
        land_data["rusticas_transactions_before"],
    )
    # 2.6. Table 'municipios'
    municipio.insert_data(land_data["municipio"])
    # 2.7. Table 'localities'
    """Before inserting the data on 'localities' table, 
    I've to retrieve the id of the 'municipio' and 'province'
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""

    municipio_id = municipio.get_municipio_id(land_data["municipio"])
    province_id = province.get_province_id(land_data["province"])

    locality.insert_data(
        land_data["locality"],
        municipio_id,
        province_id,
        land_data["population_now"],
        land_data["population_before"],
    )
    # 2.8. Table 'codigos_postales'
    codigo_postal.insert_data(land_data["codigo_postal"])
    # 2.9. Table 'delegations' is already created and populated.
    # 3.0. Table 'auctions'
    auction.insert_data(land_data["electronical_id"], land_data["auction_pdf_path"])
    # 3.1. Table 'territorios'
    territorio.insert_data(land_data["ath_number"], land_data["ath_name"])
    # 3.2. Table 'lote'
    """Before inserting the data on 'lote' table, 
    I've to retrieve the id of the 'auction'
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""
    auction_id = auction.get_auction_id(land_data["electronical_id"])
    lote.insert_data(
        auction_id,
        land_data["lote_number"],
        land_data["price"],
    )
    # 3.3. Table 'empresa'
    empresa.insert_data(land_data["empresas"])

    # 3.4 Table 'CubiertaTerrestreIberpix'
    cubierta_terrestre_iberpix.insert_data(
        land_data["usos_suelo"]["Cubierta terrestre iberpix"]
    )
    # 3.5 Table 'CubiertaTerrestreCodigee'
    cubierta_terrestre_codigee.insert_data(
        land_data["usos_suelo"]["Cubierta terrestre CODIIGE"]
    )
    # 3.6 Table 'UsosSueloHilucs'
    usos_suelo_hilucs.insert_data(land_data["usos_suelo"]["Uso del suelo HILUCS"])

    # 3.7. Table 'finca'
    """Before inserting the data on 'finca' table, 
    I've to retrieve the id of the next variables:
        1. agrupacion_cultivo_id
        2. locality_id
        3. lote_id
        4. clase_id
        5. uso_id
        6. aprovechamiento_id
        7. codigo_postal_id
        8. ath_id
        9. cubierta_terrestre_iberpix_id
        10. cubierta_terrestre_codigee_id
        11. uso_suelo_hilucs_id
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""

    ###### 3. RETRIEVING IDS FOR FINCA INSERTION ######

    # Getting the necessaries IDs of the foreign keys
    agrupacion_cultivo_id = agrupacion_cultivo.get_agrupacion_cultivo_id(
        land_data["agrupacion_cultivo"]
    )
    locality_id = locality.get_locality_id(land_data["locality"], municipio_id)
    lote_id = lote.get_lote_id(auction_id, land_data["lote_number"])
    clase_id = clase.get_clase_id(land_data["clase"])
    uso_id = uso.get_uso_id(land_data["uso"])
    aprovechamiento_id = aprovechamiento.get_aprovechamiento_id(
        land_data["aprovechamiento"]
    )
    codigo_postal_id = codigo_postal.get_codigo_postal_id(land_data["codigo_postal"])
    ath_id = territorio.get_territorio_id(land_data["ath_number"])
    cubierta_terrestre_iberpix_id = (
        cubierta_terrestre_iberpix.get_cubierta_terrestre_id(
            land_data["usos_suelo"]["Cubierta terrestre iberpix"]
        )
    )
    cubierta_terrestre_codigee_id = (
        cubierta_terrestre_codigee.get_cubierta_terrestre_id(
            land_data["usos_suelo"]["Cubierta terrestre CODIIGE"]
        )
    )
    usos_suelo_hilucs_id = usos_suelo_hilucs.get_uso_suelo_id(
        land_data["usos_suelo"]["Uso del suelo HILUCS"]
    )
    ###### 4. FINCA INSERTION ######
    data_finca_to_insert = {
        "referencia_catastral": land_data["referencia_catastral"],
        "localizacion": land_data["localizacion"],
        "catastro_value": land_data["catastro_value"],
        "delegation_id": land_data["delegation"],
        "agrupacion_cultivo_id": agrupacion_cultivo_id,
        "locality_id": locality_id,
        "lote_id": lote_id,
        "clase_id": clase_id,
        "uso_id": uso_id,
        "aprovechamiento_id": aprovechamiento_id,
        "codigo_postal_id": codigo_postal_id,
        "ath_id": ath_id,
        "cubierta_terrestre_iberpix_id": cubierta_terrestre_iberpix_id,
        "cubierta_terrestre_codigee_id": cubierta_terrestre_codigee_id,
        "uso_suelo_hilucs_id": usos_suelo_hilucs_id,
        "coordenadas": land_data["coordenadas"],
        "agrupacion_municipio": land_data["agrupacion_municipio"],
        "number_buildings": land_data["number_buildings"],
        "slope": land_data["slope"],
        "fls": land_data["fls"],
    }
    media_finca_to_insert = {
        "ortofoto": land_data["path_ortofoto_land"],
        "kml": land_data["path_kml_land"],
        "google_maps": land_data["path_googlemaps_land"],
        "curvas_nivel": land_data["fullpath_mapa_curvas_nivel"],
        "lidar": land_data["fullpath_mapa_lidar"],
        "usos_suelo": land_data["fullpath_usos_suelo"],
        "hidrografia": land_data["fullpath_ortofoto_hidrografia"],
        "report_catastro": land_data["path_report_land"],
    }
    finca.insert_data(data_finca_to_insert, media_finca_to_insert)

    ###### 5. INSERTION OF EMPRESA FINCA ######
    # 5.0. Table 'EmpresaFinca'
    """Before inserting the data on 'EmpresaFinca' table, 
    I've to retrieve the id of the next variables:
        1. finca_id      
        2. empresa_id
    that I inserted previously (they may've already exists
    on their tables, so it weren't inserted again)"""

    finca_id = finca.get_finca_id(land_data["referencia_catastral"])

    if land_data["empresas_fincas"]:
        for empresa_finca_maps in land_data["empresas_fincas"]:

            empresa_finca_cif = empresa_finca_maps["cif"]
            empresa_finca_data = empresa_finca_maps["data"]

            # Get ID of enterprise
            empresa_id = empresa.get_empresa_id(empresa_finca_cif)

            # Get relevant data
            distance_on_car = empresa_finca_data["car"]["distance_on_car"]
            time_on_car = empresa_finca_data["car"]["time_on_car"]
            distance_on_foot = empresa_finca_data["foot"]["distance_on_foot"]
            time_on_foot = empresa_finca_data["foot"]["time_on_foot"]

            # Read binary file to insert on BLOB field in table
            path_route = empresa_finca_data["path"]
            binary_content = BaseDatabase.read_binary(path_route)

            data_to_insert = {
                "empresa_id": empresa_id,
                "finca_id": finca_id,
                "distance_on_car": distance_on_car,
                "time_on_car": time_on_car,
                "distance_on_foot": distance_on_foot,
                "time_on_foot": time_on_foot,
                "route_screenshot": binary_content,
            }
            empresa_finca.insert_data(data_to_insert)

        ###### 6. DELETING FILES FROM PC (ALREADY STORED ON DB) ######

        BaseDatabase.remove_file_from_filesystem(land_data["auction_pdf_path"])
        BaseDatabase.remove_file_from_filesystem(land_data["path_ortofoto_land"])
        BaseDatabase.remove_file_from_filesystem(land_data["path_kml_land"])
        BaseDatabase.remove_file_from_filesystem(land_data["path_googlemaps_land"])
        BaseDatabase.remove_file_from_filesystem(empresa_finca_data["path"])
        BaseDatabase.remove_file_from_filesystem(
            land_data["fullpath_mapa_curvas_nivel"]
        )
        BaseDatabase.remove_file_from_filesystem(land_data["fullpath_mapa_lidar"])
        BaseDatabase.remove_file_from_filesystem(land_data["fullpath_usos_suelo"])
        BaseDatabase.remove_file_from_filesystem(
            land_data["fullpath_ortofoto_hidrografia"]
        )
        BaseDatabase.remove_file_from_filesystem(land_data["path_report_land"])
    db.close_connection()
