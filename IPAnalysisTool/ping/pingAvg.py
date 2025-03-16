from ..util.databaseUtil import connectToRemoteDB
import pandas as pd

def pingAvg(addresses = None):
    remConn, remCur = connectToRemoteDB()
    remCur.execute("""WITH non_reserved_ip AS
                       (SELECT h.ip_addr AS ip_addr FROM hosts h WHERE
                       NOT (h.ip_addr <<= '0.0.0.0/8' 
                       OR h.ip_addr <<= '0.0.0.0/32' 
                       OR h.ip_addr <<= '10.0.0.0/8' 
                        OR h.ip_addr <<= '100.64.0.0/10'
                        OR h.ip_addr <<= '127.0.0.0/8' 
                        OR h.ip_addr <<= '169.254.0.0/16' 
                        OR h.ip_addr <<= '172.16.0.0/12' 
                        OR h.ip_addr <<= '192.0.2.0/24' 
                        OR h.ip_addr <<= '192.88.99.0/24' 
                       OR h.ip_addr  <<= '192.88.99.2/32' 
                       OR h.ip_addr <<= '192.168.0.0/16' 
                        OR h.ip_addr <<= '192.0.0.0/24' 
                       OR h.ip_addr  <<= '198.18.0.0/15' 
                       OR h.ip_addr  <<= '198.51.100.0/24' 
                       OR h.ip_addr <<= '203.0.113.0/24' 
                       OR h.ip_addr <<= '255.255.255.255/32'
                        ) AND (
                            EXISTS (
                                SELECT *
                                FROM ping p
                                WHERE p.ip_addr = h.ip_addr
                                AND p.ping_ploss > 0
                                AND p.ping_ploss < 100
                            )
                        )
                    )
                   SELECT 
                       DATE(ping_date) AS date, 
                       AVG(ping_rttmin) AS ping_rttmin, 
                       AVG(ping_rttavg) AS ping_rttavg, 
                       AVG(ping_rttmax) AS ping_rttmax 
                   FROM ping
                   JOIN non_reserved_ip ON non_reserved_ip.ip_addr = ping.ip_addr
                   WHERE 
                        ping_ploss >= 0 AND 
                        ping_ploss < 100 AND 
                        /* 2009-01-01 in UNIX seconds */
                        ping_date > TO_TIMESTAMP(1230764400)
                   GROUP BY date 
                   ORDER BY date""")
    # Output data onto CSV
    # date, ping_rttmin, ping_rttavg, ping_rttmax
    data = remCur.fetchall()
    remCur.close()
    remConn.close()
    df = pd.DataFrame(data, columns=['date', 'ping_rttmin', 'ping_rttavg', 'ping_rttmax'])
    return df

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Ping Average")
    parser.add_argument("-a", "--addresses", type=str, help="IP addresses to fetch data for")
    parser.add_argument("-o", "--output", type=str, help="Output file")
    args = parser.parse_args()
    df = pingAvg(args.addresses)
    if args.output:
        df.to_csv(args.output, index=False)
    else:
        print(df)

if __name__ == "__main__":
    main()