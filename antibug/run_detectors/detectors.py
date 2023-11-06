from antibug.compile.antibug_compile.safe_dev_analyzer import SafeDevAnalyzer
from termcolor import colored
from slither_core.detectors import all_detectors
import importlib


class RunDetector(SafeDevAnalyzer):
    available_detector_list = []

    def __init__(self, input_file, detectors=None):
        self._detectors = []
        self.target = input_file
        (_, self.category, self.import_list) = self.get_all_detectors()
        self.selected_detectors = detectors if detectors is not None else []
        super().__init__(input_file)

    def get_all_detectors(self):
        importlib.reload(all_detectors)
        detector_list = [
            key for key in all_detectors.__dict__.keys() if not key.startswith('__')]
        import_list = [value for value in all_detectors.__dict__.values()]
        self.available_detector_list = detector_list
        category_list = ['Reentrancy', 'Attributes', 'CompilerBugs', 'CustomizedRules',
                         'ERC20', 'ERC721', 'Functions', 'Operations', 'Shadowing', 'Statements', 'Variables']
        for category in category_list:
            self.available_detector_list.append(category)
        return self.available_detector_list, category_list, import_list

    def register_and_run_detectors(self):
        self.available_detector_list, _, self.import_list = self.get_all_detectors()
        values = list(self.compilation_units.values())
        results = []
        for instance in values:
            if not self.selected_detectors:
                for item in self.import_list[10:]:
                    instance.register_detector(item)
                results.extend(instance.run_detectors())
            elif self.selected_detectors:
                for detector in self.selected_detectors:
                    if detector in self.category:
                        category = detector.lower()
                        filtered_list = [
                            item for item in self.import_list if f'{category}' in str(item)]
                        for item in filtered_list:
                            instance.register_detector(item)
                        results.extend(instance.run_detectors())
                    else:
                        print(colored(f'{detector} is not available', "red"))
                        exit(0)
            else:
                print(colored('No available detectors', "red"))
                exit(0)

        result = self.detect_result(results)
        return result

    def detect_result(self, results):
        results_combined = []
        if all(not sublist for sublist in results):
            print(colored("Nothing to result", "red"))
            exit(0)
        else:
            for detector_result in results:
                if detector_result:
                    print(detector_result)
                    print()
                    file_name = detector_result[0]['elements'][0]['source_mapping']['filename_absolute']
                    contract_name = detector_result[0]['elements'][0]['type_specific_fields']['parent']['name']
                    # print(contract_name)
                    function_name = detector_result[0]['elements'][0]['name']
                    # detect_line = detector_result[0]['elements'][1]['source_mapping']['lines']
                    # node = detector_result[0]['elements'][1]['name']

                    check = detector_result[0]['check']

                    impact = detector_result[0]['impact']
                    confidence = detector_result[0]['confidence']
                    descriptions = [result['description']
                                    for result in detector_result]
        #             result_combined = {'file_name': file_name, 'contract_name': contract_name,
        #                                 'function_name': function_name, 'detect_line': detect_line, 'node': node, 'check': check, 'impact': impact,
        #                                'confidence': confidence, 'description': descriptions}
        #             results_combined.append(result_combined)
        # return results_combined
