from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from termcolor import colored
from slither_core.detectors import all_detectors
import importlib
from typing import List, Type, Dict, Any, Optional
import json
import os
import logging
from slither_core.detectors.abstract_detector import classification_txt, AbstractDetector
# from slither_core.utils.output import output_to_json
from slither_core.exceptions import SlitherException
import traceback



class RunDetector(SafeDevAnalyzer):
    available_detector_list = []

    def __init__(self, input_file, detectors=None):
        self._detectors = []
        self.target = input_file
        (_, self.category, self.import_list) = self.get_all_detectors()
        self.selected_detectors = detectors if detectors is not None else []
        self.output_error = None
        self.json_results: Dict[str, Any] = {}
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
        try: 
            self.available_detector_list, _, self.import_list = self.get_all_detectors()
            values = list(self.compilation_units.values())
            results = []
            for instance in values:
                if not self.selected_detectors:
                    for item in self.import_list[10:]:
                        instance.register_detector(item)
                        
                    # results.extend(instance.run_detectors())
                    results=instance.run_detectors()
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
                            print(colored(
                                f'Error: {self.selected_detectors} is not available', 'red'))
                            return
                else:
                    print(colored(
                        f'Error: {self.selected_detectors} is not available', 'red'))
                    return
        except SlitherException as e:
            self.output_error = str(e)
            traceback.print_exc()
            logging.error(self.output_error)
        
        if all(not sublst for sublst in results):
            self.output_error = "No detection results"
            return None, self.output_error
        
        result = self.detect_result(results)
        
        return result, self.output_error

    def detect_result(self, results):
        # print(results)
        results_detectors = []
        detector_resultss = [x for x in results if x]  # remove empty results
        # print(detector_resultss)
        detector_results = [item for sublist in detector_resultss for item in sublist]  # flatten
        results_detectors.extend(detector_results)
        self.json_results = results_detectors
        # print(results_detectors)
        return self.json_results
        
