import argparse
import sys
from solc_select import solc_select
from join.rule_set.rule import RuleSet
from join.run_detectors.detectors import RunDetector
from join.run_simil.simil import Simil
from join.print_result.output import Output
from termcolor import colored
import os


def parse_arguments():
    usage = 'dream target [<args>]\n\n'
    usage += 'target can be:\n\t'
    usage += '- file path(.sol file)\n\t'
    usage += '- directory path\n\t\t'
    usage += '- supported platforms: https://github.com/crytic/crytic-compile/#crytic-compile\n\t'
    usage += '- .zip file\n\t'

    parser = argparse.ArgumentParser(
        prog='dream', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--version", help="displays the current solc version and installed list", action="store_true")

    subparsers = parser.add_subparsers(dest='command', required=False)

    # Rule Setting (Add/Remove)
    rule_parser = subparsers.add_parser('ruleset')
    rule_subparsers = rule_parser.add_subparsers(
        dest='rule_command', required=True)

    # 'add' sub-command
    add_parser = rule_subparsers.add_parser('add', help='Add a rule')
    add_parser.add_argument('file_path', help='Path to the rule file')

    # 'remove' sub-command
    remove_parser = rule_subparsers.add_parser('remove', help='Remove a rule')
    remove_parser.add_argument('rule_name', help='Name of the rule to remove')

    # Detector (Vulnerability/Logic)
    detect_parser = subparsers.add_parser('detect')
    detect_subparsers = detect_parser.add_subparsers(
        dest='detect_command', required=True)

    # 'vuln' sub-command
    vuln_parser = detect_subparsers.add_parser(
        'vuln', help='Vulnerability detector, defaults to all')
    # vuln_parser.add_argument('mode', help='Mode of the rule file.', nargs='?')
    # vuln_parser.add_argument(
    #     'fname', help='Contract and function name for similarity analysis (contract.function)', nargs='*')
    vuln_parser.add_argument('detector', help='Target rule', nargs='*')
    vuln_parser.add_argument('target', help='Path to the rule file')

    # 'logic' sub-command
    logic_parser = detect_subparsers.add_parser('logic', help='Logic detector')
    logic_parser.add_argument(
        'type', choices=['Uniswap', 'Balancer'], help='Logic detector type')
    logic_parser.add_argument('target', help='Target file')
    logic_parser.add_argument('contract', help='contract name')

    # 'all' sub-command
    all_parser = detect_subparsers.add_parser(
        'all', help='Perform both vulnerability and logic detection')
    all_parser.add_argument(
        'type', choices=['Uniswap', 'Balancer'], help='Logic detector type')
    all_parser.add_argument('target', help='Target file')
    all_parser.add_argument('contract', help='contract name')

    # Code Similar (Train/Test)
    simil_parser = subparsers.add_parser('code-similar')
    simil_subparsers = simil_parser.add_subparsers(
        dest='similar_command', required=True)

    # 'train' sub-command
    train_parser = simil_subparsers.add_parser(
        'train', help='Train a new model')
    train_parser.add_argument('model', help='Path to save the trained model')
    train_parser.add_argument('dataset', help='Path to the training dataset')

    # 'test' sub-command
    test_parser = simil_subparsers.add_parser(
        'test', help='Perform similarity test')
    test_parser.add_argument(
        'target', help='Target file for code similarity analysis')
    test_parser.add_argument(
        'fname', help='Contract and function name for similarity analysis (contract.function)')
    test_parser.add_argument(
        'detector', help='Path value of the comparison target. Specify the directory path where the comparison targets are located')
    test_parser.add_argument(
        'bin', help='Trained model used for obtaining vector values. If not provided, the default value "etherscan_verified_contracts.bin" is used', nargs='?')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def version_info():
    current_version = solc_select.current_version()
    installed_versions = solc_select.installed_versions()
    version_info = f"\nCurrent version: {current_version}\n\nInstalled versions: {installed_versions}\n"
    return version_info


def rule_set_action(action, target):
    instance = RuleSet(target)
    if action == 'add':
        instance.register_detector()
        instance.print_compared_files()
        print(colored(f"Adding ruleset for file: {target}", "green"))
    elif action == 'remove':
        instance.unregister_detector(target)
        print(colored(f"Removing ruleset for file: {target}", "green"))


def detect_vuln_simil_action(target, detector, fname):
    if not detector:
        print("Detecting all vulnerabilities")
        instance = RunDetector(target)
        result = instance.register_and_run_detectors_similmode(fname)
        instance3 = Output()
        instance3.output_logic(result)
        # for res in result:
        #     print(colored(res, "white", "on_grey"))
        # instance.print_detect_result(results)


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


def detect_logic_action(target, logic, contract):
    print("Detecting Business Logic")
    instance1 = Simil()
    similar = instance1._check_similar(target, logic, contract)

    detect_list = ['addLiquidity', 'addLiquidityETH']
    res = []
    func = []
    detc=[]
    for function in similar:
        detector_list = []
        detector = function['detector']
        if detector in detect_list:
            detector_list.append(detector)
            instance2 = RunDetector(target, detector_list)
            result = instance2.register_and_run_detectors()
            descriptions =[r['description'][0] for r in result]
            res.append(descriptions)
            func.append(function)
            detc.append(detector)
    formatted_res=[[d for d in sublist] for sublist in res]
    instance3 = Output()
    instance3.output_logic(func, formatted_res, detect_list)


def similar_train_action(model, dataset):
    print("Training New Model")
    instance = Simil()
    dataset = os.path.abspath(dataset)
    instance.train(model, dataset)


def similar_test_action(target, fname, detector, bin):
    print("Test Similarity")
    if bin is None:
        bin = os.path.abspath(
            "../join/run_simil/etherscan_verified_contracts.bin")
    else:
        bin = bin
    detector_path = os.path.abspath("../join/run_simil/Category/"+detector)
    instance = Simil()

    similar = instance.test(target, fname, detector_path, bin)
    instance2 = Output()
    instance2.output_simil(similar)


def main():
    args = parse_arguments()
    if args.version:
        print(version_info())

    elif args.command == 'ruleset':
        if hasattr(args, 'file_path'):
            target = args.file_path
        elif hasattr(args, 'rule_name'):
            target = args.rule_name
        else:
            print("Error: Invalid arguments for rule-set command.")
            return
        rule_set_action(args.rule_command, target)

    elif args.command == 'detect':
        if args.detect_command == 'vuln':
            # if args.mode == 'fast':
            detect_vuln_action(args.target, args.detector)
            # elif args.mode == 'advanced':
            #     detect_vuln_simil_action(args.target, args.detector, args.fname)
        # else:
        #     print("Error: Invalid detect mode.")
        #     return
        elif args.detect_command == 'logic':
            detect_logic_action(args.target, args.type, args.contract)
        elif args.detect_command == 'all':
            args.detector = ''
            detect_vuln_action(args.target, args.detector)
            detect_logic_action(args.target, args.type, args.contract)
        else:
            print("Error: Invalid detect command.")
            return

    elif args.command == 'code-similar':
        if args.similar_command == 'train':
            similar_train_action(args.model, args.dataset)
        elif args.similar_command == 'test':
            similar_test_action(args.target, args.fname,
                                args.detector, args.bin)
        else:
            print("Error: Invalid code-similar command.")
            return

    else:
        print("Error: Invalid command.")


if __name__ == '__main__':
    main()
