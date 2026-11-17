import argparse
import glob
import os
import sys
from pathlib import Path
from imgutils.tagging.pixai import get_pixai_tags

SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

def collect_image_files(target_path: str, recursive: bool = False) -> list[str]:
    path = Path(target_path)
    if path.is_dir():
        pattern = '**/*' if recursive else '*'
        return [
            str(p) for p in sorted(path.glob(pattern))
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ]
    elif path.is_file():
        return [str(path)]
    else:
        matched = glob.glob(target_path, recursive=recursive)
        return [
            p for p in sorted(matched)
            if os.path.isfile(p) and Path(p).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ]

def extract_tags(pixai_result, character_first: bool = False) -> list[str]:
    """get_pixai_tags の戻り値（(general_dict, character_dict) または辞書）からタグ名のリストを抽出する"""
    if isinstance(pixai_result, tuple):
        if len(pixai_result) == 2 and isinstance(pixai_result[0], dict) and isinstance(pixai_result[1], dict):
            general_dict, character_dict = pixai_result
            if character_first:
                first, second = character_dict, general_dict
            else:
                first, second = general_dict, character_dict
            combined = list(first.keys()) + [t for t in second.keys() if t not in first]
            return combined
        else:
            tag_list = []
            for item in pixai_result:
                if isinstance(item, dict):
                    tag_list.extend(item.keys())
                elif isinstance(item, str):
                    tag_list.append(item)
            return list(dict.fromkeys(tag_list))
    elif isinstance(pixai_result, dict):
        return list(pixai_result.keys())
    elif isinstance(pixai_result, list):
        return list(pixai_result)
    return []

def main():
    parser = argparse.ArgumentParser(description='PixAIモデルでタギングを行います')
    parser.add_argument('--image-path', type=str, required=True, help='タギングする画像ファイル、ディレクトリ、またはglobパターンのパス')
    parser.add_argument('-r', '--recursive', action='store_true', help='ディレクトリ内の画像を再帰的に検索する')
    parser.add_argument('-t', '--threshold', type=float, default=None, help='タグ判定の閾値（省略時はモデルのデフォルト値）')
    parser.add_argument('--character-first', action='store_true', help='キャラクタータグを先頭に配置する')
    parser.add_argument('-p', '--prefix-tags', type=str, nargs='*', default=[], help='前方（先頭）に追加するタグのリスト（トリガーワードなど）')
    parser.add_argument('-i', '--ignore-tags', type=str, nargs='*', default=[], help='無視するタグのリスト')
    parser.add_argument('-a', '--additional-tags', type=str, nargs='*', default=[], help='後方（末尾）に追加するタグのリスト')
    parser.add_argument('-s', '--save-txt', action='store_true', help='画像と同名の .txt ファイルにタグを出力する')

    args = parser.parse_args()

    image_files = collect_image_files(args.image_path, recursive=args.recursive)
    if not image_files:
        print(f"No image files found for path: {args.image_path}", file=sys.stderr)
        return

    ignore_tags_set = set(args.ignore_tags)

    for image_file in image_files:
        try:
            kwargs = {}
            if args.threshold is not None:
                kwargs['thresholds'] = args.threshold

            pixai_result = get_pixai_tags(image_file, **kwargs)
            raw_tags = extract_tags(pixai_result, character_first=args.character_first)

            detected_tags = [tag for tag in raw_tags if tag not in ignore_tags_set]

            # prefix_tags -> detected_tags -> additional_tags の順で重複なく結合
            tags = []
            for tag in args.prefix_tags:
                if tag not in tags:
                    tags.append(tag)

            for tag in detected_tags:
                if tag not in tags:
                    tags.append(tag)

            for tag in args.additional_tags:
                if tag not in tags:
                    tags.append(tag)

            tag_line = ', '.join(tags)
            print(f"Image: {image_file}", flush=True)
            print(f"Tags: {tag_line}", flush=True)

            if args.save_txt:
                txt_path = Path(image_file).with_suffix('.txt')
                txt_path.write_text(tag_line, encoding='utf-8')

        except Exception as e:
            print(f"Error processing {image_file}: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
