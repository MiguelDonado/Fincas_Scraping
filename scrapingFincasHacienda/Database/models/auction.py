import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Auction(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "auctions" (
                "id" INTEGER,
                "electronical_id" TEXT UNIQUE,   
                "pliego_pdf" BLOB,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, electronical_id, path_pdf):
        # If the argument is None, then do nothing
        if not electronical_id:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_auction_id(electronical_id):

            # Get the binary contents of the PDF to insert them on the BLOB field
            pliego_pdf = Db.BaseDatabase.read_binary(path_pdf)

            sql = """
                    INSERT INTO "auctions"
                    ("electronical_id","pliego_pdf")
                    VALUES (:electronical_id,:pliego_pdf)
                    """
            params = {
                "electronical_id": electronical_id,
                "pliego_pdf": pliego_pdf,
            }
            self.execute_query(sql, params)

    def get_auction_id(self, electronical_id):
        sql = 'SELECT "id" FROM auctions WHERE "electronical_id"=:electronical_id'
        params = {"electronical_id": electronical_id}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
