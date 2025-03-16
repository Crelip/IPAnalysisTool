from os.path import expanduser


def connectToRemoteDB():
    import psycopg2
    import os
    import yaml
    configFolder = os.path.expanduser("~/.config/IPAnalysisTool")
    if not os.path.exists(configFolder):
        os.makedirs(configFolder)
    config = None
    try:
        with open(configFolder + "/config.yml", "r") as f:
            config = yaml.safe_load(f)
    except:
        from .setupUtil import setupDatabaseLogin
        setupDatabaseLogin()

    try:
        remConn = psycopg2.connect(
            "dbname=" + config["database_name"] + " user=" + config["database_user"] + " password=" + config[
                "database_password"] + " host=" + config["database_host"])
    except:
        print("Error connecting to the database. Please check your login details.")
        exit(1)
    remCur = remConn.cursor()
    return remConn, remCur

def connectToLocalDB():
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

    locConn = sqlite3.connect(expanduser("~/.cache/IPAnalysisTool/data.db"))
    locCur = locConn.cursor()
    return locConn, locCur