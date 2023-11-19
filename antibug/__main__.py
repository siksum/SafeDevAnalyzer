import argparse
import sys
import argparse
import subprocess

from antibug.utils.convert_to_json import convert_to_compile_info_json, convert_to_detect_result_json, remove_all_json_files, convert_to_contract_analysis_info_json
from antibug.utils.audit_report import export_to_markdown
from antibug.run_detectors.detectors import RunDetector

from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from antibug.compile.parse_version_and_install_solc import SolcParser
from antibug.run_security_report.app import main as audit_report
from antibug.run_printer.printer import contract_analysis
from antibug.run_printer.printer import RunPrinter


from streamlit.web.cli import main_run

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
    # detect_parser.add_argument('language', help='Language of the description', nargs='?')
    detect_parser.add_argument('detector', help='Target rule', nargs='*')
    detect_parser.add_argument('target', help='Path to the rule file')
    
    remove_parser = subparsers.add_parser('remove')
    
    # 'deploy' sub-command
    compile_parser = subparsers.add_parser(
        'compile', help='antibug compiler, defaults to all')
    compile_parser.add_argument('target', help='ath to the rule file')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def version_info():
    solc_parser = SolcParser()
    current_version = solc_parser.current_solc_version
    installed_versions = solc_parser.intalled_solc_versions
    version_info = f"\nCurrent version: {current_version}\n\nInstalled versions: {installed_versions}\n"
    return version_info


def detect_vuln_action(analyzer, detector):
    if not detector:
        print("Detecting all vulnerabilities")
        instance = RunDetector(analyzer)
        result_list, filename, error = instance.register_and_run_detectors()
        
    else:
        print("Detecting specific vulnerabilities")
        instance = RunDetector(analyzer, detector)
        result_list, filename, error = instance.register_and_run_detectors()
  
    return result_list, filename, error


def main():
    args = parse_arguments()
    analyzer = SafeDevAnalyzer(args.target)
    
    if args.command == 'compile':
        abi_list, bytecode_list = analyzer.to_compile()
        convert_to_compile_info_json(abi_list, bytecode_list, analyzer)
        
    elif args.command == 'detect':
        try:
            # contract analysis -> json
            combined_data = contract_analysis(analyzer)
            convert_to_contract_analysis_info_json(combined_data, analyzer)
            
            # call graph -> png
            printer = RunPrinter(analyzer, 'call-graph')
            printer.register_and_run_printers()
            printer.convert_dot_to_png()
            
            result_list, filename, error = detect_vuln_action(analyzer, args.detector)
            ret= convert_to_detect_result_json(result_list, filename, error, analyzer)
            if ret != 0:
                export_to_markdown(args.target)
        except Exception as e:
            print(str(e)) 

    elif args.command == 'remove':
        remove_all_json_files()
        
    else:
        print("Error: Invalid command.")
        return


if __name__ == '__main__':
    main()

