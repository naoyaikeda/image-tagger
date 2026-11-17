import argparse
import glob
import sys
from imgutils.tagging.pixai import get_pixai_tags

def main():
    parser = argparse.ArgumentParser(description = 'PixAIモデルでタギングを行います')
    parser.add_argument('--image-path', type=str, required=True, help='タギングする画像のパス')
    parser.add_argument('-i', '--ignore-tags', type=str, nargs='*', default=[], help='無視するタグのリスト')
    parser.add_argument('-a', '--additional-tags', type=str, nargs='*', default=[], help='追加するタグのリスト')

    args = parser.parse_args()

    image_path = args.image_path

    for image_file in glob.glob(image_path):
        try:
            tags = get_pixai_tags(image_file)
            tags = [tag for tag in tags if tag not in args.ignore_tags]
            tags.extend(args.additional_tags)
            print(f"Image: {image_file}")
            print(f"Tags: {', '.join(tags)}")
        except Exception as e:
            print(f"Error processing {image_file}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
