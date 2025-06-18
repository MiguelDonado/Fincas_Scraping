import sqlite3
import sys
from pathlib import Path

import Database.constants as const
import Database.models.base_database as Db
import regex


class Empresa(Db.BaseDatabase):

    # Class attributes
    columns_names_insert_sql = Db.BaseDatabase.generate_insert_statement_columns(
        "Empresa"
    )
    values_placeholders_sql = (
        Db.BaseDatabase.generate_insert_statement_values_placeholders("Empresa")
    )

    def __init__(self):
        self.__create_table()  # If the table is already created, it does nothing

    def __create_table(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS "empresas" (
                "id" INTEGER, 
                {const.EMPRESAS_HEADERS}
                PRIMARY KEY ("id")
            )    
            """
        self.execute_query(sql)

    def insert_data(self, df):
        # If the argument is None, then do nothing
        if df is None:
            return None
        sql = f'INSERT INTO "empresas" ({self.columns_names_insert_sql}) VALUES ({self.values_placeholders_sql})'

        # The for loop iterates over the rows of the DataFrame using itertuples
        # (index=False, name=None), which returns each row as a tuple
        # without the index
        headers = self.get_columns_names_list(
            "Empresa"
        )  # Get the headers from the dataframe
        headers = [header.replace('"', "") for header in headers]
        for row in df.itertuples(index=False, name=None):
            # Before inserting the data, check if already exists on the table
            # If it doesn't exists, then proceed to insert it
            if not self.get_empresa_id(row[1]):
                # Create a dictionary where keys are headers and values are row data
                row_dict = dict(zip(headers, row))
                self.execute_query(sql, row_dict)

    def get_empresa_id(self, nif):
        sql = 'SELECT "id" FROM empresas WHERE "Código NIF"=:nif'
        params = {"nif": nif}
        self.execute_query(sql, params)
        result = self.cursor.fetchone()
        return result["id"] if result else None

    def delete_data(self, nif):
        sql = 'DELETE FROM empresas WHERE "Código NIF"=:nif'
        params = {"nif": nif}
        self.execute_query(sql, params)

    def testing_purposes(self):
        sql = 'SELECT "id" FROM empresas'
        result = self.execute_query(sql)
        return result["id"] if result else None

    # def __update_data(self): Won't have a method for updating data because it has no sense for this dimension table
    # the street and the financial ratios dont need to be updated till several years go by
