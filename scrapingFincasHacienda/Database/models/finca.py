import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Finca(Db.BaseDatabase):

    columns_names_insert_sql = Db.BaseDatabase.generate_insert_statement_columns(
        "Finca"
    )
    values_placeholders_sql = (
        Db.BaseDatabase.generate_insert_statement_values_placeholders("Finca")
    )

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "fincas" (
            "id" INTEGER, 
            {const.FINCA_HEADERS}
            PRIMARY KEY ("id"),
            FOREIGN KEY ("delegation_id") REFERENCES "delegations"("id"),
            FOREIGN KEY ("agrupacion_cultivo_id") REFERENCES "agrupacion_cultivos"("id"),
            FOREIGN KEY ("locality_id") REFERENCES "localities"("id"),
            FOREIGN KEY ("lote_id") REFERENCES "lotes"("id"),
            FOREIGN KEY ("clase_id") REFERENCES "clases"("id"),
            FOREIGN KEY ("uso_id") REFERENCES "usos"("id"),
            FOREIGN KEY ("aprovechamiento_id") REFERENCES "aprovechamientos"("id"),
            FOREIGN KEY ("codigo_postal_id") REFERENCES "codigos_postales"("id"),
            FOREIGN KEY ("ath_id") REFERENCES "territorios"("id"),
            FOREIGN KEY ("cubierta_terrestre_iberpix_id") REFERENCES "cubiertas_terrestres_iberpix"("id"),
            FOREIGN KEY ("cubierta_terrestre_codigee_id") REFERENCES "cubiertas_terrestres_codigee"("id"),
            FOREIGN KEY ("uso_suelo_hilucs_id") REFERENCES "usos_suelo_hilucs"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self,
        data,
        file_paths,
    ):
        # If the argument is None, then do nothing
        if not data["referencia_catastral"]:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_finca_id(data["referencia_catastral"]):
            for key, path in file_paths.items():
                data[key] = Db.BaseDatabase.read_binary(path)
            sql = f'INSERT INTO "fincas" ({self.columns_names_insert_sql}) VALUES ({self.values_placeholders_sql})'
            self.execute_query(sql, data)

    def get_finca_id(self, ref):
        sql = 'SELECT "id" FROM fincas WHERE "referencia_catastral"=:ref'
        params = {"ref": ref}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
