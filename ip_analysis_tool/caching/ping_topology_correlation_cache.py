from ..util.database_util import connect_to_local_db, connect_to_remote_db

def ping_topology_correlation_cache(address):
    rem_conn, rem_cur = connect_to_remote_db()
    loc_conn, loc_cur = connect_to_local_db()
    # Get ping and topology measurements from days during which there was both a successful ping and topology measurement.
    rem_cur.execute(f"""SELECT p.ip_addr, date(t.t_date) AS date, p.ping_rttmin, p.ping_rttavg, p.ping_rttmax, t.t_hops FROM ping p JOIN topology t ON p.ip_addr = t.ip_addr AND date(t.t_date) = date(p.ping_date)
    WHERE p.ip_addr = cidr '{address}/32' AND date(t.t_date) >= date '2009-01-01' AND p.ping_ploss < 100 AND p.ping_ploss >= 0 AND t.t_status <> 'E' ORDER BY date ASC;""")
    loc_cur.execute(
        "CREATE TABLE IF NOT EXISTS ip_ping_topology_cor (ip_addr text, t_date date, ping_rttmin real, ping_rttavg real, ping_rttmax real, t_hops integer);")
    for record in rem_cur:
        loc_cur.execute("INSERT INTO ip_ping_topology_cor VALUES (?, ?, ?, ?, ?, ?);", tuple(record))
    loc_conn.commit()
    rem_cur.close()
    rem_conn.close()
    loc_cur.close()
    loc_conn.close()

def main(address):
    ping_topology_correlation_cache(address)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Ping-Topology Correlation Cache")
    parser.add_argument("-a", "--address", type=str, help="IP address to fetch data for")
    args = parser.parse_args()
    main(args.address)