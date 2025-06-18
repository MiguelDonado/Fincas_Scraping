import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class CubiertaTerrestreCodigee(
    Db.BaseDatabase
):  # Descripcion Cubierta Terrestre s/Codigee
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "cubiertas_terrestres_codigee" (
                "id" INTEGER, 
                "cubierta_terrestre" TEXT NOT NULL UNIQUE,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, cubierta_terrestre):
        # If the argument is None, then do nothing
        if not cubierta_terrestre:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_cubierta_terrestre_id(cubierta_terrestre):
            sql = """
                    INSERT INTO "cubiertas_terrestres_codigee" 
                    ("cubierta_terrestre")
                    VALUES (:cubierta_terrestre)
                    """
            params = {"cubierta_terrestre": cubierta_terrestre}
            self.execute_query(sql, params)

    def get_cubierta_terrestre_id(self, cubierta_terrestre):
        sql = 'SELECT "id" FROM "cubiertas_terrestres_codigee" WHERE "cubierta_terrestre"=:cubierta_terrestre'
        params = {"cubierta_terrestre": cubierta_terrestre}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
