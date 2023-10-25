import os
import ast
import slither_core.detectors.all_detectors as all_detectors
import re
from .pysimilarity import PySimilarity
from join.run_detectors.detectors import RunDetector
from termcolor import colored


class RuleSet():
    detector_list = []

    def __init__(self, target: str) -> None:
        if target.endswith(".py"):
            self.file_path = os.path.abspath(target)
            self.file_name = os.path.basename(target)
            self.class_name = self.extract_class_names()
            self.source = self.get_source_code(self.file_path)
        self.detector_list = self.get_all_detectors()
        self.detector_path = os.path.abspath(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "../../slither_core/detectors/"))

    def extract_class_names(self):
        with open(self.file_path, "r") as file:
            tree = ast.parse(file.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names = node.name
        return class_names

    def get_all_detectors(self):
        detector_list = [
            key for key in all_detectors.__dict__.keys() if not key.startswith('__')]
        self.detector_list = detector_list
        return self.detector_list

    def get_source_code(self, target):
        with open(target, "r") as file:
            source = file.read()
        return source

    def register_detector(self) -> None:
        detector_path = os.path.join(
            self.detector_path+"/vulnerability/customized_rules/"+self.file_name)
        if os.path.exists(detector_path):
            print(f"File '{detector_path}' already exists.")
            exit(0)
        self.detector_list.append(self.class_name)
        with open(detector_path, "w") as file:
            file.write(self.source)
        print(f"File '{detector_path}' created.")
        self._add_all_detectors()

    def _add_all_detectors(self) -> None:
        with open(all_detectors.__file__, "r") as file:
            content = file.readlines()
        add_line = f"from .vulnerability.customized_rules.{self.file_name[:-3]} import {self.class_name}\n"
        if add_line in content:
            print(f"{self.class_name} is already in all_detectors.py")
            exit(0)
        content.append(
            f"\nfrom .vulnerability.customized_rules.{self.file_name[:-3]} import {self.class_name}\n")

        with open(all_detectors.__file__, "w") as file:
            file.writelines(content)
        print(
            colored(f"{self.class_name} is added to all_detectors.py", "green"))

    def unregister_detector(self, target) -> None:
        detector_path = self._remove_all_detectors(target)
        if os.path.exists(detector_path):
            self.detector_list.remove(target)
            os.remove(detector_path)
            print(colored(f"File '{detector_path}' deleted.", "green"))
        else:
            print(colored(f"File '{detector_path}' does not exist.", "red"))
            exit(0)

    def _remove_all_detectors(self, target) -> None:
        detector_path = ""
        with open(all_detectors.__file__, "r") as file:
            content = file.read()
        import_pattern = rf".*import {re.escape(target)}"
        import_line = re.findall(import_pattern, content)
        import_line = ''.join(import_line)

        content = content.split("\n")

        if import_line in content:
            content.remove(import_line)
            content.pop(0)
            detector_path = os.path.join(
                self.detector_path, "vulnerability/customized_rules/", target+".py")
            with open(all_detectors.__file__, "w") as file:
                file.write('\n'.join(content))
            print(
                colored(f"{target} is removed from all_detectors.py", "green"))
        else:
            print(
                colored(f"{target} is not imported in all_detectors.py", "red"))
            exit(0)
        return detector_path

    def print_compared_files(self):
        py_similarity = PySimilarity(self.file_name)
        (origin_detector, origin_detector_contents,
         _) = py_similarity.compare_files()
        example_path = os.path.abspath(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "rule_compare_examples", origin_detector + ".sol"))

        origin_result = RunDetector(example_path, [origin_detector])
        origin_detect_result = origin_result.register_and_run_detectors()

        new_result = RunDetector(
            example_path, [py_similarity.new_detector[:-3]])
        new_detect_result = new_result.register_and_run_detectors()

        print(colored(f"Origin Detector: {origin_detector}", "magenta"))
        print(colored(f"Origin Detector Result:", "magenta"))
        for description in origin_detect_result:
            print(
                colored(f"detector: {description['check']}", "white", "on_grey"))
            for des in description['description']:
                print(colored(des, "cyan", "on_grey"))

        print(
            colored(f"\nNew Detector: {py_similarity.new_detector[:-3]}", "yellow"))
        print(colored(f"New Detector Result:", "yellow"))
        for description in new_detect_result:
            print(
                colored(f"detector: {description['check']}", "white", "on_grey"))
            for des in description['description']:
                print(colored(des, "cyan", "on_grey"))

        # result = [
        #     ["",self.py_similarity.new_detector[:-3], origin_detector],
        #     ["Contents", self.py_similarity.new_detector_content, origin_detector_contents],
        #     ["Run Result", new_detect_result, origin_detect_result]
        # ]
        # table = tabulate(result, tablefmt="fancy_grid")
        # print(table)

        # tabulate 사용시 셀이 깨져버리는 현상 발생 -> tabulate는 고정 값을 갖고 있어 내용이 길어지면 셀이 깨짐


# rule = RuleSet("Dream.py")
# print(rule.detector_list)
# rule.register_detector()
# rule.print_compared_files()


# rule2 = RuleSet("Reentrant.py")
# print(rule2.detector_list)
# rule2.unregister_detector("Reentrant")
# print(rule2.detector_list)
