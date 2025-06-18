import sqlite3
from pathlib import Path

import regex

import Database.constants as const


class BaseDatabase:
    _shared_borg_state = {}

    # Implementing Borg Singleton
    # State sharing for different instances. https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__dict__ = cls._shared_borg_state
        return obj

    def __init__(self, db_name=const.DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Enable named tuple access
        self.cursor = self.connection.cursor()

    # Two main variables:
    # 1) "columns": Refers to the columns specified on the query (a method is used get the columns from the query into a list)
    # 2) "params": Refers to the dictionary that is passed as the second argument of a prepared SQL statement.
    #              Example: sql = 'INSERT INTO "aprovechamientos" ("aprovechamiento") VALUES (:aprovechamiento)'
    #                       params = {"aprovechamiento": aprovechamiento} # Esto de aqui
    #                       self.execute_query(sql, params)

    def execute_query(self, query, params=None):
        with self.connection:
            if not params:
                self.cursor.execute(query)
            else:
                if "INSERT INTO" in query:
                    columns_list = (
                        regex.search(const.DEBUG_COLUMNS_PATTERN, query)
                        .group(1)
                        .replace('"', "")
                    )
                    columns_list = regex.split(r",\s*", columns_list)
                    params_list = params.keys()
                    assert len(columns_list) == len(params_list), (
                        f"Mismatch between columns and parameters: "
                        f"{len(columns_list)} columns vs {len(params_list)} parameters"
                        f"{self.explain_differences_prepared_sql_statement(columns_list, list(params_list))}"
                    )
                self.cursor.execute(query, params)

    def close_connection(self):
        if self.connection:
            self.connection.close()

    # Method to check if the connection is closed
    def is_connection_closed(self):
        try:
            self.connection.execute("SELECT 1")
            return False
        except sqlite3.ProgrammingError:
            return True

    #####
    ########
    ############# HELPER FUNCTIONS (USED BY THE CHILD CLASSES)
    ########
    #####
    @staticmethod
    def explain_differences_prepared_sql_statement(columns, params):
        diffs = set(columns).symmetric_difference(list(params))

        columns_diffs = []
        params_diffs = []

        for diff in diffs:
            if diff in columns:
                columns_diffs.append(diff)
            else:
                params_diffs.append(diff)

        msg = (
            f"\n> The 'columns' in the query have the next extra values {columns_diffs}"
            f"\n> The 'params' have the next extra values {params_diffs}"
        )
        return msg

    @staticmethod
    def read_binary(path_binary_file):
        # If the path to the binary file is empty.
        # i.e. when a land doesnt have the report from the catastro
        # the path_report_catastro'll be None
        if not path_binary_file:
            return None
        with open(path_binary_file, "rb") as file:
            binary_file = file.read()
        return binary_file

    @staticmethod
    def remove_file_from_filesystem(path):
        if path:
            file_path = Path(path)
            try:
                file_path.unlink()
            except Exception:
                return None
        else:
            return None

    # ================= Used by 'EmpresaFinca', 'Finca' and 'Empresa' classes =================
    # ================== to dinamically generate INSERT statements =================
    #
    # Because the number of columns of this classes is big, instead of doing it manually,
    # its better they are generated dinamically, and insert statements are more maintainable.

    @staticmethod
    def generate_insert_statement_columns(caller_class_name: str):
        assert caller_class_name in [
            "EmpresaFinca",
            "Finca",
            "Empresa",
        ], "caller_class_name must be 'EmpresaFinca', 'Finca' or 'Empresa'"
        columns_names_list = BaseDatabase.get_columns_names_list(caller_class_name)
        column_names_insert_statement = ", ".join(columns_names_list)
        return column_names_insert_statement

    @staticmethod
    def generate_insert_statement_values_placeholders(caller_class_name: str):
        assert caller_class_name in [
            "EmpresaFinca",
            "Finca",
            "Empresa",
        ], "caller_class_name must be 'EmpresaFinca', 'Finca' or 'Empresa'"
        # Get values placeholders to dynamically create the SQL statements
        columns_names_list = BaseDatabase.get_columns_names_list(caller_class_name)
        values_placeholders_list = [":" + column for column in columns_names_list]
        values_placeholders = ", ".join(values_placeholders_list).replace('"', "")
        return values_placeholders

    #### Helper method used by 'generate_insert_statement_columns' and 'generate_insert_statement_values_placeholders'
    @staticmethod
    def get_columns_names_list(caller_class_name: str):
        assert caller_class_name in [
            "EmpresaFinca",
            "Finca",
            "Empresa",
        ], "caller_class_name must be 'EmpresaFinca', 'Finca' or 'Empresa'"

        if caller_class_name == "EmpresaFinca":
            headers = const.EMPRESAS_FINCAS_HEADERS
        elif caller_class_name == "Finca":
            headers = const.FINCA_HEADERS
        elif caller_class_name == "Empresa":
            headers = const.EMPRESAS_HEADERS

        # Get columns names to dynamically create SQL statement
        columns_names_list = regex.findall(const.COLUMNS_PATTERN, headers)
        columns_names_list = [column.strip() for column in columns_names_list]

        # Because the last column in Finca table is the timestamp
        # I dont neet to include it on the insert statement
        if caller_class_name == "Finca":
            return columns_names_list[:-1]
        elif caller_class_name in ["EmpresaFinca", "Empresa"]:
            return columns_names_list
