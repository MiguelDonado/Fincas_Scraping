import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class CodigoPostal(Db.BaseDatabase):  # Código Postal
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "codigos_postales" (
                "id" INTEGER, 
                "codigo_postal" TEXT NOT NULL UNIQUE,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, codigo_postal):
        # If the argument is None, then do nothing
        if not codigo_postal:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_codigo_postal_id(codigo_postal):
            sql = """
                    INSERT INTO "codigos_postales" 
                    ("codigo_postal")
                    VALUES (:codigo_postal)
                    """
            params = {"codigo_postal": codigo_postal}
            self.execute_query(sql, params)

    def get_codigo_postal_id(self, codigo_postal):
        sql = 'SELECT "id" FROM "codigos_postales" WHERE "codigo_postal"=:codigo_postal'
        params = {"codigo_postal": codigo_postal}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
