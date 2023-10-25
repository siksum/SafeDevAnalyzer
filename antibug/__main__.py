import argparse
import sys
from solc_select import solc_select
from antibug.rule_set.rule import RuleSet
from antibug.run_detectors.detectors import RunDetector
# from antibug.run_simil.simil import Simil
from antibug.print_result.output import Output
from termcolor import colored
import os
from antibug.antibug_compile.compile import SafeDevAnalyzer
import json

def parse_arguments():
    usage = 'antibug target [<args>]\n\n'
    usage += 'target can be:\n\t'
    usage += '- file path(.sol file)\n\t'
    usage += '- directory path\n\t\t'
    usage += '- supported platforms: https://github.com/crytic/crytic-compile/#crytic-compile\n\t'

    parser = argparse.ArgumentParser(
        prog='antibug', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--version", help="displays the current solc version and installed list", action="store_true")

    subparsers = parser.add_subparsers(dest='command', required=False)

    # Detector (Vulnerability/Logic)
    detect_parser = subparsers.add_parser('detect')
    detect_subparsers = detect_parser.add_subparsers(
        dest='detect_command', required=True)

    # 'vuln' sub-command
    vuln_parser = detect_subparsers.add_parser(
        'vuln', help='Vulnerability detector, defaults to all')
    vuln_parser.add_argument('detector', help='Target rule', nargs='*')
    vuln_parser.add_argument('target', help='Path to the rule file')

    # 'deploy' sub-command
    deploy_parser = detect_subparsers.add_parser(
        'deploy', help='Deploy detector, defaults to all')
    deploy_parser.add_argument('target', help='ath to the rule file')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def version_info():
    current_version = solc_select.current_version()
    installed_versions = solc_select.installed_versions()
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
        # instance.print_detect_result(results)

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

        # instance.print_detect_result(results)

def get_root_dir():
    current_working_directory = os.getcwd()
    while not os.path.basename(current_working_directory) == "safe_dev_analyzer":
        current_working_directory = os.path.dirname(current_working_directory)
    return current_working_directory


def convert_to_json(abi_list, bytecode_list, analyzer:SafeDevAnalyzer):
    combined_data = {}

    output_dir = os.path.join(get_root_dir(), "json_results")
    print(output_dir)
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
    if args.version:
        print(version_info())
        return
    elif args.command == 'detect':
        if args.detect_command == 'vuln':
            detect_vuln_action(args.target, args.detector)
        else:
            print("Error: Invalid detect mode.")
            return
    elif args.command == 'deploy':
        analyzer = SafeDevAnalyzer(args.target)
        abi_list, bytecode_list = analyzer.to_deploy()
        convert_to_json(abi_list, bytecode_list, analyzer)

    else:
        print("Error: Invalid command.")
        return


if __name__ == '__main__':
    main()
