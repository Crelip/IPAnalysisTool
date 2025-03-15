def connectToRemoteDB():
    import psycopg2
    from dotenv import load_dotenv
    from os import environ
    load_dotenv()
    remConn = psycopg2.connect(
        "dbname=" + environ["IP_DBNAME"] + " user=" + environ["IP_USER"] + " password=" + environ[
            "IP_PASSWORD"] + " host=" + environ["IP_HOST"])
    remCur = remConn.cursor()
    return remConn, remCur

def connectToLocalDB():
    import sqlite3
    import datetime

    # Define an adapter to convert datetime.date to string
    def adapt_date(val: datetime.date) -> str:
        return val.isoformat()

    # Define a converter to convert a string back to datetime.date
    def convert_date(val: bytes) -> datetime.date:
        return datetime.date.fromisoformat(val.decode("utf-8"))

    # Register the adapter and converter for date types
    sqlite3.register_adapter(datetime.date, adapt_date)
    sqlite3.register_converter("DATE", convert_date)

    from os.path import expanduser
    locConn = sqlite3.connect(expanduser("~/.cache/IPAnalysisTool/data.db"))
    locCur = locConn.cursor()
    return locConn, locCur