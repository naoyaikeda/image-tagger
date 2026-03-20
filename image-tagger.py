import sys
from imgutils.tagging.pixai import get_pixai_tags

def main():
    filename = sys.argv[1]
    print(filename)
    tags = get_pixai_tags(filename)
    print(tags)

if __name__ == "__main__":
    main()
