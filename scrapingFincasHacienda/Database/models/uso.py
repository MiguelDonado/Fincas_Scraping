import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Uso(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        self.__populate_table()  # If the table is already populated, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "usos" (
                "id" INTEGER,
                "uso_resumido" TEXT NOT NULL,
                "uso_completo" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def __populate_table(self):
        sql = "SELECT * FROM usos"
        # Check if the table already contains data
        self.execute_query(sql)
        is_populated = self.cursor.fetchone()

        # Only populate if the table is empty
        if not is_populated:
            for uso_resumido, uso_completo in const.ALLOWED_USOS.items():
                self.__insert_data(uso_resumido, uso_completo)

    def __insert_data(self, uso_resumido, uso_completo):
        sql = 'INSERT INTO "usos" ("uso_resumido", "uso_completo") VALUES (:resumido, :completo)'
        params = {"resumido": uso_resumido.lower(), "completo": uso_completo.lower()}
        self.execute_query(sql, params)

    def get_uso_id(self, uso_resumido):
        sql = 'SELECT "id" FROM "usos" WHERE "uso_resumido"=:uso_resumido'
        params = {"uso_resumido": uso_resumido.lower()}
        self.execute_query(sql, params)
        return self.cursor.fetchone()["id"]

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)
