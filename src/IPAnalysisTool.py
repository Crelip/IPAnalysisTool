import sys
def main():
    if sys.argv[1] == "graphCache":
        from graphCache import main as graphCache
        graphCache(sys.argv[2:])
    elif sys.argv[1] == "timeSeriesAnalysis":
        from timeSeriesAnalysis import main as timeSeriesAnalysis
        timeSeriesAnalysis(sys.argv[2:])
    else:
        print("Invalid command")
        sys.exit(1)
if __name__ == "__main__":
    main()