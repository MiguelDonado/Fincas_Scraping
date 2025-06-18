import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Clase(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        self.__populate_table()  # If the table is already populated, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "clases" (
                "id" INTEGER,
                "clase" TEXT NOT NULL,
                PRIMARY KEY ("id")                               
            )
            """
        self.execute_query(sql)

    def __populate_table(self):
        # Check if the table already contains data
        sql = 'SELECT * FROM "clases"'
        self.execute_query(sql)
        is_populated = self.cursor.fetchone()

        # Only populate if the table is empty
        if not is_populated:
            for clase in const.ALLOWED_CLASES:
                self.__insert_data(clase)

    def __insert_data(self, clase):
        sql = 'INSERT INTO "clases" ("clase") VALUES (:clase)'
        params = {"clase": clase.lower()}
        self.execute_query(sql, params)

    def get_clase_id(self, clase):
        sql = 'SELECT * FROM "clases" WHERE "clase"=:clase'
        params = {"clase": clase.lower()}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)
