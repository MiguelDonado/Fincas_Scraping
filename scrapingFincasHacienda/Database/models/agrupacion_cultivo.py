import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class AgrupacionCultivo(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "agrupacion_cultivos" (
                "id" INTEGER,
                "agrupacion_cultivo" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )        
"""
        self.execute_query(sql)

    def insert_data(self, agrupacion_cultivo):
        # If the argument is None, then do nothing
        if not agrupacion_cultivo:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_agrupacion_cultivo_id(agrupacion_cultivo):
            sql = 'INSERT INTO "agrupacion_cultivos" ("agrupacion_cultivo") VALUES (:agrupacion_cultivo)'
            params = {"agrupacion_cultivo": agrupacion_cultivo}
            self.execute_query(sql, params)

    def get_agrupacion_cultivo_id(self, agrupacion_cultivo):
        sql = 'SELECT id FROM "agrupacion_cultivos" WHERE "agrupacion_cultivo"=:agrupacion_cultivo'
        params = {"agrupacion_cultivo": agrupacion_cultivo}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
