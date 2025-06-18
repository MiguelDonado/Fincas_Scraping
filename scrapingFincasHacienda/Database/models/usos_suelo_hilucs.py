import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class UsosSueloHilucs(Db.BaseDatabase):  # Descripcion Usos del Suelo s/Hilucs
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "usos_suelo_hilucs" (
                "id" INTEGER, 
                "uso_suelo" TEXT NOT NULL UNIQUE,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, uso_suelo):
        # If the argument is None, then do nothing
        if not uso_suelo:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_uso_suelo_id(uso_suelo):
            sql = """
                    INSERT INTO "usos_suelo_hilucs" 
                    ("uso_suelo")
                    VALUES (:uso_suelo)
                    """
            params = {"uso_suelo": uso_suelo}
            self.execute_query(sql, params)

    def get_uso_suelo_id(self, uso_suelo):
        sql = 'SELECT "id" FROM "usos_suelo_hilucs" WHERE "uso_suelo"=:uso_suelo'
        params = {"uso_suelo": uso_suelo}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
