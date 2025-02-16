import graph_tool.all as gt
import os
import datetime
from collections import defaultdict
from json import dumps
from util.weekUtil import getWeek


def kcoreDecomposition(date: datetime.date):
    inputFile : str = os.path.expanduser(f'''~/.cache/IPAnalysisTool/graphs/week/{datetime.datetime.strftime(getWeek(date)[0], "%Y-%m-%d")}.gt''')
    g : gt.Graph = gt.load_graph(inputFile)
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
    parser = ArgumentParser()
    parser.add_argument("-d", "--date", help="Generates data for the week containing the given date.")
    args = parser.parse_args()
    print(dumps(kcoreDecomposition(datetime.datetime.strptime(args.date, "%Y-%m-%d").date())))

if __name__ == "__main__":
    main()