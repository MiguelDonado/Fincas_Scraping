import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Province(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "provinces" (
                "id" INTEGER, 
                "province" TEXT NOT NULL,
                "rusticas_transactions_now" INTEGER,
                "rusticas_transactions_before" INTEGER,
                PRIMARY KEY ("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self, province, rusticas_transactions_now, rusticas_transactions_before
    ):
        # If the argument is None, then do nothing
        if not province:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_province_id(province):
            sql = """
                    INSERT INTO "provinces" 
                    ("province","rusticas_transactions_now","rusticas_transactions_before")
                    VALUES (:province, :rusticas_transactions_now, :rusticas_transactions_before)
                """
            params = {
                "province": province,
                "rusticas_transactions_now": rusticas_transactions_now,
                "rusticas_transactions_before": rusticas_transactions_before,
            }
            self.execute_query(sql, params)

    def get_province_id(self, province):
        sql = """SELECT id FROM "provinces" WHERE "province"=:province"""
        params = {"province": province}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the transactions statistics) but they dont need to be updated till several years go by
