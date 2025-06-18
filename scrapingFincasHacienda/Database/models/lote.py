import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Lote(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "lotes" (
                "id" INTEGER,
                "auction_id" INTEGER,
                "lote_number" INTEGER,
                "price" INTEGER,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("auction_id") REFERENCES "auctions"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(self, auction_id, lote_number, price):
        # If the argument is None, then do nothing
        if not auction_id:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_lote_id(auction_id, lote_number):
            sql = """
                    INSERT INTO "lotes" 
                    ("auction_id","lote_number","price")
                    VALUES (:auction_id, :lote_number, :price)
                    """
            params = {
                "auction_id": auction_id,
                "lote_number": lote_number,
                "price": price,
            }
            self.execute_query(sql, params)

    def get_lote_id(self, auction_id, lote_number):
        sql = 'SELECT "id" FROM lotes WHERE auction_id=:auction_id AND lote_number=:lote_number'
        params = {"auction_id": auction_id, "lote_number": lote_number}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
