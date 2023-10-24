from join.compile.compile import Join
from termcolor import colored
from slither_core.detectors import all_detectors
import importlib
from join.run_simil.simil import Simil
import os


class RunDetector(Join):
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
                    elif detector in self.available_detector_list:
                        filtered_list = [
                            item for item in self.import_list if f'{detector}' in str(item)]
                        if detector == 'addLiquidity':
                            filtered_list.pop()
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

    def register_and_run_detectors_similmode(self, fname):
        simil = Simil()
        simil_result = []
        cache_path = os.path.abspath(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "../run_simil/cache.npz"))
        bin_path = os.path.join(os.path.dirname(
            __file__), "../run_simil/etherscan_verified_contracts.bin")
        for function in fname:
            results = simil.test(
                self.target_path, function, cache_path, bin_path)
            for result in results:
                simil_result.append({
                    'target': function,
                    'detect': f'{result[1]}.{result[2]}',
                    'score': result[3],
                })
        return simil_result

    def detect_result(self, results):
        results_combined = []
        if all(not sublist for sublist in results):
            print(colored("Nothing to result", "red"))
            exit(0)
        else:
            for detector_result in results:
                if detector_result:
                    check = detector_result[0].get('check')
                    impact = detector_result[0]['impact']
                    confidence = detector_result[0]['confidence']
                    descriptions = [result['description']
                                    for result in detector_result]
                    result_combined = {'check': check, 'impact': impact,
                                       'confidence': confidence, 'description': descriptions}
                    results_combined.append(result_combined)
        return results_combined


# d = RunDetector('./re-entrancy.sol', ['Dream'])
# d.run_and_print_detectors()
