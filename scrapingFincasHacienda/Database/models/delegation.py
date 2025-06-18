import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Delegation(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing
        self.__populate_table()  # If the table is already populated, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "delegations" (
                "id" INTEGER,
                "delegation" TEXT NOT NULL,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def __populate_table(self):
        # Check if the table already contains data
        sql = "SELECT * FROM delegations"
        self.execute_query(sql)
        is_populated = self.cursor.fetchone()

        # Only populate if the table is empty
        if not is_populated:
            for delegation in const.DELEGATIONS:
                delegation = const.DELEGATION_MAPPING[str(delegation)]
                self.__insert_data(delegation)

    def __insert_data(self, delegation):
        sql = 'INSERT INTO "delegations" ("delegation") VALUES (:delegation)'
        params = {"delegation": delegation}
        self.execute_query(sql, params)

    # def __delete_data(self): Won't have a method for deleting data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def __update_data(self): Won't have a method for updating data because
    # it's a dimension table that stores static data (CONSTANTS)

    # def get_delegation_xxxx(self): Won't have a method for selecting data because
    # to insert data into the fincas table (delegation_id column),
    # I need to first retrieve the id from the delegations table,
    # but on this case I already have the id.
