import argparse
import sys
from imgutils.tagging.pixai import get_pixai_tags

def main():
    parser = argparse.ArgumentParser(description = 'PixAIモデルでタギングを行います')

    args = parser.parse_args()

if __name__ == "__main__":
    main()
