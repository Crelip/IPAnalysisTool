import graph_tool.all as gt
import datetime
from collections import defaultdict
from util.graphGetter import getGraphByDate


def kcoreDecomposition(date: datetime.date):
    g : gt.Graph = getGraphByDate(date)
    kcore = gt.kcore_decomposition(g)
    groups = defaultdict(list)
    maxK = 0
    for v in g.vertices():
        k = kcore[v]
        groups[k].append(g.vp.ip[v])
        if k > maxK: maxK = k
    return {
        "date": datetime.datetime.strftime(date, "%Y-%m-%d"),
        "maxK": maxK,
        "decomposition": [
            {
                "kcore": i,
                "count": len(groups[i]),
                "IPs": groups[i]
            } for i in range(maxK + 1) if i in groups.keys()
        ]
    }

def main():
    from argparse import ArgumentParser
    from json import dumps
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    args = parser.parse_args()
    print(dumps(kcoreDecomposition(datetime.datetime.strptime(args.date, "%Y-%m-%d").date())))

if __name__ == "__main__":
    main()