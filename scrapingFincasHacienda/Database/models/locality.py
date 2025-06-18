import sqlite3
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Locality(Db.BaseDatabase):
    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "localities" (
                "id" INTEGER,
                "locality" TEXT NOT NULL,
                "municipio_id" TEXT NOT NULL,
                "province_id" TEXT NOT NULL,
                "population_now" INTEGER,
                "population_before" INTEGER,
                PRIMARY KEY ("id"),
                FOREIGN KEY ("municipio_id") REFERENCES "municipios"("id"),
                FOREIGN KEY ("province_id") REFERENCES "provinces"("id")
            )
            """
        self.execute_query(sql)

    def insert_data(
        self, locality, municipio_id, province_id, population_now, population_before
    ):
        # If the argument is None, then do nothing
        if not locality:
            return None
        # Before inserting the data, check if already exists on the table
        # If it doesn't exists, then proceed to insert it
        if not self.get_locality_id(locality, municipio_id):
            sql = """
                    INSERT INTO "localities" 
                    ("locality", "municipio_id", "province_id", "population_now", "population_before") 
                    VALUES (:locality, :municipio_id, :province_id, :population_now, :population_before)
                    """
            params = {
                "locality": locality,
                "municipio_id": municipio_id,
                "province_id": province_id,
                "population_now": population_now,
                "population_before": population_before,
            }
            self.execute_query(sql, params)

    def get_locality_id(self, locality, municipio_id):
        sql = 'SELECT "id" FROM "localities" WHERE "locality"=:locality AND "municipio_id"=:municipio_id'
        params = {"locality": locality, "municipio_id": municipio_id}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    # def __delete_data(self): Won't have a method for deleting data because it has no sense for this dimension table
    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # (maybe for the population statistics) but they dont need to be updated till several years go by
