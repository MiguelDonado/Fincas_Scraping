import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Territorio(Db.BaseDatabase):  # ATH (agrupacion territorio homogeneo)
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "territorios" (
                "id" INTEGER,
                "ath_number" INTEGER NOT NULL,
                "ath_name" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, ath_number, ath_name):
        # If the argument is None, then do nothing
        if not ath_number:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_territorio_id(ath_number):
            sql = """
                    INSERT INTO "territorios" 
                    ("ath_number","ath_name")
                    VALUES (:ath_number, :ath_name)
                    """
            params = {"ath_number": ath_number, "ath_name": ath_name}
            self.execute_query(sql, params)

    def get_territorio_id(self, ath_number):
        sql = 'SELECT "id" FROM territorios WHERE "ath_number"=:ath_number'
        params = {"ath_number": ath_number}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
