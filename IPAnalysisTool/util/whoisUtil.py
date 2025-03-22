import sqlite3
from datetime import datetime
import json
from os.path import expanduser
from ..util.database_util import connect_to_local_db

class WhoIsDatabase:
    def __init__(self):
        self.conn, self.cursor = connect_to_local_db()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS whois_data (
                ip TEXT PRIMARY KEY,
                data TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def insert_or_update(self, ip, data):
        timestamp = datetime.utcnow().isoformat()
        self.cursor.execute('''
            INSERT INTO whois_data (ip, data, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(ip) DO UPDATE SET
                data=excluded.data,
                timestamp=excluded.timestamp
        ''', (ip, json.dumps(data), timestamp))
        self.conn.commit()

    def fetch(self, ip):
        self.cursor.execute('SELECT data FROM whois_data WHERE ip = ?', (ip,))
        result = self.cursor.fetchone()
        return json.loads(result[0]) if result else None

    def close(self):
        self.conn.close()

from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError

class WhoIs:
    def __init__(self):
        self.db = WhoIsDatabase()

    def lookup(self, ip):
        data = self.db.fetch(ip)
        if data is None:
            try:
                obj = IPWhois(ip)
                data = obj.lookup_rdap()
                self.db.insert_or_update(ip, data)
            except IPDefinedError:
                data = {"error": "Invalid IP address"}
                self.db.insert_or_update(ip, data)
            except Exception as e:
                data = {"error": str(e)}
                self.db.insert_or_update(ip, data)
        return data

    def close(self):
        self.db.close()
