import pandas as pd
from ..enums import TimeInterval

def ping_topology_latency_correlation(time_interval: TimeInterval, verbose : bool = False) -> pd.DataFrame:
    """
    Simple function for testing the correlation between the ping latency data from the database and the topology latency data from the topology. It collects data for all endpoints across the entire data range split into intervals.
    :param time_interval: The interval to use for the data collection.
    :param verbose: If true, prints info on the console. Default is False.
    :return: Dataframe containing the average latency from topology, ping and their ratios for each date.
    """
    from ..util.date_util import get_cache_date_range
    from ..util.graph_getter import get_graph_by_date
    from ..util.date_util import iterate_range, get_date_string
    from ..util.database_util import connect_to_remote_db
    range = get_cache_date_range(time_interval)
    conn, cur = connect_to_remote_db()
    
    dates = []
    topology_latencies = []
    ping_latencies = []
    ratios = []
    
    for start, end in iterate_range(range[0], range[1], time_interval):
        g = get_graph_by_date(start, time_interval=time_interval)
        # Get the avg latency data for the endpoints
        latencies = [g.vp["avg_distance"][v] for v in g.vertices() if g.vp.position_in_route[v] == 2]
        avg_latency = (sum(latencies) / len(latencies)) if len(latencies) > 0 else 0
        # Get the avg latency data for the endpoints from the database
        endpoint_ips = [f"{g.vp.ip[v]}/32"
                        for v in g.vertices()
                        if g.vp.position_in_route[v] == 2]

        query = """
                SELECT AVG(ping_rttavg) / 2 AS avg_db_latency
                FROM ping
                WHERE ping_date >= %s
                AND ping_date <= %s
                AND ip_addr = ANY (%s::cidr[]) \
                """
        params = [start, end, endpoint_ips]

        cur.execute(query, params)
        avg_db_latency = cur.fetchone()[0]
        if avg_db_latency is None or avg_db_latency > 1000000: avg_db_latency = None
        if avg_latency == 0: avg_latency = None
        dates.append(get_date_string(start))
        topology_latencies.append(avg_latency)
        ping_latencies.append(avg_db_latency)
        ratio = (avg_db_latency / avg_latency) if (avg_latency is not None and avg_db_latency is not None) else 0
        ratios.append(ratio)
        if verbose:
            print("{} {}: Topology Latency: {}ms, DB Latency: {}ms, Ratio: {}".format(
                  str(time_interval), get_date_string(start), avg_latency, avg_db_latency, ratio))

    cur.close()
    conn.close()
    data = {
        "date": dates,
        "topology_latency": topology_latencies,
        "ping_latency": ping_latencies,
        "ratio": ratios
    }
    return pd.DataFrame(data)