import argparse
import sys
import zipfile
import shutil
import os
from crytic_compile import cryticparser
from slither_core.slither import Slither
from join.compile.solc_parse.parser import parse as solc_parse
from slither_core.tools.flattening.flattening import (
    Flattening,
    Strategy,
    STRATEGIES_NAMES,
)


def parse_args() -> argparse.Namespace:
    """
    Parse the underlying arguments for the program.
    :return: Returns the arguments for the program.
    """
    parser = argparse.ArgumentParser(
        description="Contracts flattening. See https://github.com/crytic/slither/wiki/Contract-Flattening",
        usage="join-flat filename",
    )

    parser.add_argument(
        "filename", help="The filename of the contract or project to analyze.")

    parser.add_argument(
        "--contract", help="Flatten one contract.", default=None)

    parser.add_argument(
        "--path", help="export library path to root path.", default=None)

    parser.add_argument(
        "--strategy",
        help=f"Flatenning strategy: {STRATEGIES_NAMES} (default: MostDerived).",
        default=Strategy.MostDerived.name,  # pylint: disable=no-member
    )

    # Add default arguments from crytic-compile
    cryticparser.init(parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def execute(filename, args, strategy):
    slither = Slither(filename, **vars(args))
    for compilation_unit in slither.compilation_units:
        flat = Flattening(compilation_unit)
        try:
            strategy = Strategy[strategy]
        except KeyError:
            print("KeyError")
            return
        flat.export(strategy=strategy)


def search_file(directory, file_name):
    file_paths = ''
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name == file_name:
                file_paths = os.path.join(root, name)
    return file_paths


def search_parent_directory(directory):
    pattern = '@openzeppelin'
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != '__MACOSX']
        for dir_name in dirs:
            if dir_name.startswith(pattern):
                # 상위 디렉토리 경로 반환
                return os.path.abspath(os.path.join(root, dir_name, ".."))
            elif dir_name == "node_modules":
                return os.path.abspath(os.path.join(root, dir_name))

    raise ValueError(f"'{pattern}'로 시작하는 디렉토리를 찾을 수 없습니다.")


def extract_from_zip(path):
    # 압축 파일명을 사용하여 output_directory 설정
    file_name = os.path.splitext(os.path.basename(path))[0]
    output_directory = os.path.join('.', file_name)

    # 압축 해제할 디렉토리가 없으면 생성
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with zipfile.ZipFile(path, 'r') as zip_ref:
        # 압축 파일 해제
        zip_ref.extractall(output_directory)

    # 압축 해제된 디렉토리 경로를 반환한다.
    return output_directory


def main() -> None:
    args = parse_args()
    print(args)

    if os.path.isdir(args.filename):
        file = search_file(args.filename, args.contract)
        solc_parse(file)
        export_path = search_parent_directory(args.filename)
        print(export_path)
        args.solc_remaps = f"@={export_path}/@"
        execute(file, args, args.strategy)
    elif (os.path.isfile(args.filename)):
        if (args.filename.endswith('.sol')):
            solc_parse(args.filename)
            args.solc_remaps = f"@={args.path}/@"
            execute(args.filename, args, args.strategy)
        elif (args.filename.endswith('.zip')):
            extracted_directory = extract_from_zip(args.filename)
            search_file_path = search_file(extracted_directory, args.contract)
            solc_parse(search_file_path)
            export_lib_path = search_parent_directory(extracted_directory)
            args.solc_remaps = f"@={export_lib_path}/@"
            execute(search_file_path, args, args.strategy)
            shutil.rmtree(extracted_directory)
        else:
            print('Not supported file type')
            sys.exit(0)
    else:
        print('Not supported file type')
        sys.exit(0)


if __name__ == "__main__":
    main()
