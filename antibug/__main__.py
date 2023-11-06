import argparse
import sys
from termcolor import colored
import argparse

from antibug.utils.convert_to_json import convert_to_deploy_info_json, convert_to_detect_result_json, convert_to_blacklist_result_json
from antibug.run_detectors.detectors import RunDetector
from antibug.run_detectors.based_blacklist.test import test
from antibug.run_detectors.based_blacklist.vuln import vuln

from antibug.compile.compile import SafeDevAnalyzer
from antibug.compile.parse_version_and_install_solc import SolcParser



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
    detect_subparser = detect_parser.add_subparsers(dest='detect_command', required=True)

    basic_parser = detect_subparser.add_parser('basic')
    basic_parser.add_argument('detector', help='Target rule', nargs='*')
    basic_parser.add_argument('target', help='Path to the rule file')

    blacklist_parser = detect_subparser.add_parser('blacklist')
    blacklist_parser.add_argument("model", help="model.bin")
    blacklist_parser.add_argument("filename", action="store", help="contract.sol")
    blacklist_parser.add_argument("fname", action="store", help="Target function")
    blacklist_parser.add_argument("input", action="store", help="File or directory used as input")
    blacklist_parser.add_argument(
        "--ntop",
        action="store",
        type=int,
        default=10,
        help="Number of more similar contracts to show for testing",
    )

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
        return result
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
            print()
        return result
    
def detect_based_blacklist_action(target, fname, input, bin):
    filename, contract, fname, res = test(target, fname, input, bin)

    target_info = {
        # "model" : model,
        "filename" : filename,
        "contract" : contract,
        "fname" : fname
    }

    similarity = []

    for key, value in res.items():
        path, contract, function = key
        score = float(value)
        if score >= 0.9:
            vuln_type, severity, etherscan, description = vuln(path)
            with open(path, "r") as code_files:
                code_content = "```solidity\n" + code_files.read() + "```"
            entry = {
                "vulneability_type" : vuln_type,
                "severity" : severity,
                "path" : path,
                "code" : code_content,
                "contract" : contract,
                "function" : function,
                "score" : score,
                "etherscan" : etherscan,
                "description" : description
            }
            similarity.append(entry)
    
    result = {
        "target" : [target_info],
        "similarity" : similarity
    }
    return result, contract, fname


def main():
    args = parse_arguments()
    if args.command == 'detect':
        if args.detect_command == 'basic':
            result = detect_vuln_action(args.target, args.detector)
            convert_to_detect_result_json(result, args.target)
        elif args.detect_command == 'blacklist':
            result, contract, function = detect_based_blacklist_action(args.filename, args.fname, args.input, args.model)
            convert_to_blacklist_result_json(result, contract, function)
        else:
            print("Error: Invalid command.")
            return
    elif args.command == 'deploy':
        analyzer = SafeDevAnalyzer(args.target)
        abi_list, bytecode_list = analyzer.to_deploy()
        convert_to_deploy_info_json(abi_list, bytecode_list, analyzer)
    else:
        print("Error: Invalid command.")
        return


if __name__ == '__main__':
    main()

