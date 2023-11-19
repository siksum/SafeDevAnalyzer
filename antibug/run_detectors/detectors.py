
import importlib
import logging
import traceback

from typing import Dict, Any

from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from slither_core.exceptions import SlitherException
from slither_core.detectors import all_detectors

class RunDetector():
    available_detector_list = []

    def __init__(self, safe_dev_analyzer: "SafeDevAnalyzer", detectors=None):
        self._detectors = []
        self.file = safe_dev_analyzer.file_basename
        (_, self.category, self.import_list) = self.get_all_detectors()
        self.selected_detectors = detectors if detectors is not None else []
        self.output_error = []
        self.json_results: Dict[str, Any] = {}
        self.safe_dev_analyzer = safe_dev_analyzer

    def get_all_detectors(self):
        importlib.reload(all_detectors)
        detector_list = [
            key for key in all_detectors.__dict__.keys() if not key.startswith('__')]
        import_list = [value for value in all_detectors.__dict__.values()]
        self.available_detector_list = detector_list
        category_list = ['Assembly','Reentrancy', 'Randomness', 'CompilerBugs', 'CustomizedRules',
                         'ERC20', 'ERC721', 'Functions', 'Operations', 'Shadowing', 'Statements', 'Variables']
        for category in category_list:
            self.available_detector_list.append(category)
        return self.available_detector_list, category_list, import_list

    def register_and_run_detectors(self):
        try: 
            self.available_detector_list, _, self.import_list = self.get_all_detectors()
            compilation_unit_list = list(self.safe_dev_analyzer.compilation_units.values())
            results = []
            result=[]
            compilation_units_detect_results=[]
            for compilnation_unit in compilation_unit_list:
                if not self.selected_detectors:
                    for item in self.import_list[10:]:
                        compilnation_unit.register_detector(item)
                    results=compilnation_unit.run_detectors()
                    
                elif self.selected_detectors:
                    for detector in self.selected_detectors:
                        if detector in self.category:
                            category = detector.lower()
                            filtered_list = [
                                item for item in self.import_list if f'{category}' in str(item)]
                            for item in filtered_list:
                                compilnation_unit.register_detector(item)
                            results.append(compilnation_unit.run_detectors())
                        elif detector in self.available_detector_list:
                            compilnation_unit.register_detector(
                                self.import_list[self.available_detector_list.index(detector)])
                            results.append(compilnation_unit.run_detectors())
                        else:
                            print(f'Error: {self.selected_detectors} is not available')
                            return
                        
                else:
                    print(f'Error: {self.selected_detectors} is not available')
                    return
                
                if all(not sublst for sublst in results):
                    self.output_error.append("No detection results")
                    compilation_units_detect_results.append(None)
                    return compilation_units_detect_results, self.file_list, self.output_error, 
                result=self.detect_result(results)
                self.output_error.append(None)    
                
        except SlitherException as e:
            self.output_error=str(e)
            traceback.print_exc()
            logging.error(self.output_error)
        
        return result, self.file, self.output_error

    def detect_result(self, results):
        results_detectors = []
        detector_resultss = [x for x in results if x]  # remove empty results
        detector_results = [item for sublist in detector_resultss for item in sublist]  # flatten
        results_detectors.extend(detector_results)
        self.json_results = results_detectors
        return self.json_results
        
    # @property
    # def detector_high(self):
    #     return [len(compilation_unit.detectors_high) for compilation_unit in self.compilation_units.values()]
            
    
    # @property
    # def detector_medium(self):
    #     return [len(compilation_unit.detectors_medium) for compilation_unit in self.compilation_units.values()]

        
    # @property
    # def detector_low(self):
    #     return [len(compilation_unit.detectors_low) for compilation_unit in self.compilation_units.values()]
