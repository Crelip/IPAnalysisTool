import datetime
from typing import Tuple
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

# Gets the earliest and latest date in the database
def get_database_range() -> Tuple[datetime.date, datetime.date]:
    """
    Returns the earliest and latest date found in the remote database.
    :return: The earliest and latest date found in the remote database.
    """
    # Database connection setup
    rem_conn, rem_cur = connect_to_remote_db()

    # Get the earliest date
    rem_cur.execute("SELECT MIN(t_date) FROM topology")
    record = rem_cur.fetchone()
    earliest_date = record[0]

    # Get the latest date
    rem_cur.execute("SELECT MAX(t_date) FROM topology")
    record = rem_cur.fetchone()
    latest_date = record[0]

    rem_cur.close()
    rem_conn.close()

    return earliest_date, latest_date