import sys
def main():
    if sys.argv[1] == "graphCache":
        from IPAnalysisTool.caching.graphCache import main as graphCache
        graphCache(sys.argv[2:])
    elif sys.argv[1] == "timeSeriesAnalysis":
        from timeSeriesAnalysis import main as timeSeriesAnalysis
        timeSeriesAnalysis(sys.argv[2:])
    else:
        print("""Welcome to IPAnalysisTool!
        In order to use its features, you must provide other arguments.""")
        sys.exit(1)
if __name__ == "__main__":
    main()