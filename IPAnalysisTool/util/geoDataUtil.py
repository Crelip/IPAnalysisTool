from typing import Iterable
def get_geo_data(ips: Iterable[str]) -> dict[str, dict]:
    from os.path import expanduser
    from os import scandir
    try:
        with scandir(expanduser("~/.cache/IPAnalysisTool/geo_data")) as files:
            for file in files:
                if file.name.endswith(".mmdb"):
                    geo_data = file.path
                    break
    except:
        print("Geo data not found. Download the IP To City Lite database in the MMDB form from https://db-ip.com/db/download/ip-to-city-lite and put it in the folder ~/.cache/IPAnalysisTool/geo_data/")
        return None

    from maxminddb import open_database
    with open_database(geo_data) as db:
        print("Geo data loaded successfully. IP Geolocation by DB-IP: https://dp-ip.com")
        def get_geo_single(ip):
            try:
                return db.get(ip)
            except:
                return None

        return {ip: get_geo_single(ip) for ip in ips}