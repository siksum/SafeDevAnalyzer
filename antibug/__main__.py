import argparse
import sys
from antibug.run_detectors.detectors import RunDetector
# from antibug.run_simil.simil import Simil
#from antibug.print_result.output import Output
from termcolor import colored
import os
from antibug.antibug_compile.compile import SafeDevAnalyzer
from antibug.antibug_compile.parse_version_and_install_solc import SolcParser

import json
import glob

def parse_arguments():
    usage = 'antibug target [<args>]\n\n'
    usage += 'target can be:\n\t'
    usage += '- file path(.sol file)\n\t'
    usage += '- directory path\n\t\t'
    usage += '- supported platforms: https://github.com/crytic/crytic-compile/#crytic-compile\n\t'

    parser = argparse.ArgumentParser(
        prog='antibug', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument(
    #     "--version", help="displays the current solc version and installed list", action="store_true")

    subparsers = parser.add_subparsers(dest='command', required=False)

    # Detector (Vulnerability/Logic)
    detect_parser = subparsers.add_parser('detect')
    detect_parser.add_argument('detector', help='Target rule', nargs='*')
    detect_parser.add_argument('target', help='Path to the rule file')

    # 'deploy' sub-command
    deploy_parser = subparsers.add_parser(
        'deploy', help='Deploy detector, defaults to all')
    deploy_parser.add_argument('target', help='ath to the rule file')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def version_info():
    solc_parser = SolcParser()
    current_version = solc_parser.get_current_version()
    installed_versions = solc_parser.get_intalled_versions()
    version_info = f"\nCurrent version: {current_version}\n\nInstalled versions: {installed_versions}\n"
    return version_info


def detect_vuln_action(target, detector):
    if not detector:
        print("Detecting all vulnerabilities")
        instance = RunDetector(target)
        result = instance.register_and_run_detectors()
        for res in result:
            print(colored(f"check: {res['check']}", "magenta"))
            print(colored(f"impact: {res['impact']}", "magenta"))
            print(colored(f"confidence: {res['confidence']}", "magenta"))
            print(colored(f"description", "magenta"))
            for description in res['description']:
                print(colored(description, "cyan"), end=' ')
            print()

    else:
        print("Detecting specific vulnerabilities")
        instance = RunDetector(target, detector)
        result = instance.register_and_run_detectors()
        for res in result:
            print(colored(f"check: {res['check']}", "magenta"))
            print(colored(f"impact: {res['impact']}", "magenta"))
            print(colored(f"confidence: {res['confidence']}", "magenta"))
            print(colored(f"description", "magenta"))
            for description in res['description']:
                print(colored(description, "cyan"), end=' ')


def get_root_dir():
    current_working_directory = os.getcwd()
    while not os.path.basename(current_working_directory) == "safe_dev_analyzer":
        current_working_directory = os.path.dirname(current_working_directory)
    return current_working_directory

def convert_to_json(abi_list, bytecode_list, analyzer:SafeDevAnalyzer):
    combined_data = {}

    output_dir = os.path.join(get_root_dir(), "json_results")
    print(output_dir)

    # Delete all files inside the output directory
    files = glob.glob(os.path.join(output_dir, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to delete {f}. Reason: {e}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for abi, bytecode, filename in zip(abi_list, bytecode_list, analyzer.target_list):
        filename=os.path.basename(filename)[:-4]
        key = next(iter(abi))
        combined_data[key] = {
            "contract": key,
            "abis": abi[key],
            "bytecodes": "0x" + bytecode[key]
        }
        combined_json = json.dumps(combined_data[key], indent=2)
        try:
            output_path = os.path.join(output_dir+f"/{filename}.json")
            with open(output_path, "w") as f:
                f.write(combined_json)
        except Exception as e:
            print(f"Failed to write to {output_path}. Reason: {e}")


def main():
    args = parse_arguments()
    if args.command == 'detect':
        detect_vuln_action(args.target, args.detector)

    elif args.command == 'deploy':
        analyzer = SafeDevAnalyzer(args.target)
        abi_list, bytecode_list = analyzer.to_deploy()
        convert_to_json(abi_list, bytecode_list, analyzer)

    else:
        print("Error: Invalid command.")
        return


if __name__ == '__main__':
    main()
