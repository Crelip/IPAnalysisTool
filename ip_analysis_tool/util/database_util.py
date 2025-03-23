def connect_to_remote_db() -> tuple:
    """
    Connect to the remote database using the login details stored in ~/.config/ip_analysis_tool/config.yml
    :return: tuple of the psycopg2 connection and cursor objects
    """
    import psycopg2
    import os
    import yaml
    config_folder = os.path.expanduser("~/.config/IPAnalysisTool")
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    config = None
    try:
        with open(config_folder + "/config.yml", "r") as f:
            config = yaml.safe_load(f)
    except:
        from .setup_util import setup_database_login
        setup_database_login()

    try:
        rem_conn = psycopg2.connect(
            "dbname=" + config["database_name"] + " user=" + config["database_user"] + " password=" + config[
                "database_password"] + " host=" + config["database_host"])
    except:
        print("Error connecting to the database. Please check your login details.")
        exit(1)
    rem_cur = rem_conn.cursor()
    return rem_conn, rem_cur

def connect_to_local_db() -> tuple:
    """
    Connect to the local SQLite database
    :return: tuple of the sqlite3 connection and cursor objects
    """
    import sqlite3
    import datetime
    from os.path import expanduser

    # Define an adapter to convert datetime.date to string
    def adapt_date(val: datetime.date) -> str:
        return val.isoformat()

    # Define a converter to convert a string back to datetime.date
    def convert_date(val: bytes) -> datetime.date:
        return datetime.date.fromisoformat(val.decode("utf-8"))

    # Register the adapter and converter for date types
    sqlite3.register_adapter(datetime.date, adapt_date)
    sqlite3.register_converter("DATE", convert_date)

    loc_conn = sqlite3.connect(expanduser("~/.cache/IPAnalysisTool/data.db"))
    loc_cur = loc_conn.cursor()
    return loc_conn, loc_cur