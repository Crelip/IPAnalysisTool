import argparse
import sys

# All utility imports
from graphCache import main as graphCache
from timeSeriesAnalysis import main as timeSeriesAnalysis

def main():
    if sys.argv[1] == "graphCache":
        graphCache(sys.argv[2:])
    elif sys.argv[1] == "timeSeriesAnalysis":
        print(sys.argv)
        timeSeriesAnalysis(sys.argv[2:])
    else:
        print("Invalid command")
        sys.exit(1)
if __name__ == "__main__":
    main()