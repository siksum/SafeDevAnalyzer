
import logging
import traceback
import inspect

from typing import Dict, Any

from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from slither_core.exceptions import SlitherException
from slither_core.detectors import all_detectors
from slither_core.detectors.abstract_detector import AbstractDetector

class RunDetector():
    def __init__(self, safe_dev_analyzer: "SafeDevAnalyzer", detectors=None):
        self._detectors = []
        self.file = safe_dev_analyzer.file_basename
        self.import_list = self.get_all_detectors_import_list()
        self.available_detector, self.category_list = self.available_detectors()
        self.output_error = []
        self.json_results: Dict[str, Any] = {}
        self.selected_detectors = detectors if detectors is not None else []
        self.safe_dev_analyzer = safe_dev_analyzer

    def get_all_detectors_import_list(self):
        import_list_ = [getattr(all_detectors, name) for name in dir(all_detectors)]
        import_list = [d for d in import_list_ if inspect.isclass(d) and issubclass(d, AbstractDetector)]
        return import_list
    

    def available_detectors(self):
        detectors={d.ARGUMENT: d for d in self.import_list}
        category_list = ['Assembly','Reentrancy', 'Randomness', 'Delegatecall', 'DoS', 'Ownership', 'SelfDestruct', 'Operations']
        for category in category_list:
            filtered_list = [
                item for item in self.import_list if f'{category.lower()}' in str(item)]
            detectors[category] = filtered_list
        return detectors, category_list


    def register_and_run_detectors(self):
        try: 
            compilation_unit_list = list(self.safe_dev_analyzer.compilation_units.values())
            results = []
            result=[]
        
            compilation_units_detect_results=[]
            for compilnation_unit in compilation_unit_list:
                if not self.selected_detectors:
                    for item in self.import_list:
                        compilnation_unit.register_detector(item)
                    results=compilnation_unit.run_detectors()
                elif self.selected_detectors:
                    for detector in self.selected_detectors:
                        if detector in self.category_list:
                            for item in self.available_detector[detector]:
                                compilnation_unit.register_detector(item)
                            results.append(compilnation_unit.run_detectors())
                        elif detector in self.available_detector.keys():
                            compilnation_unit.register_detector(
                                self.available_detector[detector])
                            results.append(compilnation_unit.run_detectors())
                        else:
                            print(f'Error: {self.selected_detectors} is not available')
                            return
                        
                else:
                    print(f'Error: {self.selected_detectors} is not available')
                    return
            # if all((not inner_list for inner_list in sublist) for sublist in results):
            #     self.output_error.append("No detection results")
            #     compilation_units_detect_results.append(None)
            #     return compilation_units_detect_results, self.safe_dev_analyzer.file_list, self.output_error, 
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
