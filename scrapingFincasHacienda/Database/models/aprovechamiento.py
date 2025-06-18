import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Aprovechamiento(Db.BaseDatabase):  # Cultivo / aprovechamiento
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "aprovechamientos" (
                "id" INTEGER, 
                "aprovechamiento" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, aprovechamiento):
        # If the argument is None, then do nothing
        if not aprovechamiento:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_aprovechamiento_id(aprovechamiento):
            sql = 'INSERT INTO "aprovechamientos" ("aprovechamiento") VALUES (:aprovechamiento)'
            params = {"aprovechamiento": aprovechamiento}
            self.execute_query(sql, params)

    def get_aprovechamiento_id(self, aprovechamiento):
        sql = (
            'SELECT id FROM "aprovechamientos" WHERE "aprovechamiento"=:aprovechamiento'
        )
        params = {"aprovechamiento": aprovechamiento}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
