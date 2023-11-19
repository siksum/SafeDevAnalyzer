from slither_core.slither import Slither

from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer   
from slither_core.printers import all_printers
from slither_core.printers.abstract_printer import AbstractPrinter
import inspect
import graphviz
import os

class RunPrinter(SafeDevAnalyzer):
    def __init__(self, input_file):
        super().__init__(input_file)
        self.printer_list = self.get_all_printers()
        self.selected_printer = ""
        self.filename = os.path.basename(input_file)[:-4]
        
    def get_all_printers(self):
        printers_ = [getattr(all_printers, name) for name in dir(all_printers)]
        printers = [p for p in printers_ if inspect.isclass(p) and issubclass(p, AbstractPrinter)]
        return printers

    def choose_printer(self, printer_name):
        printers = {p.ARGUMENT: p for p in self.printer_list}
        if printer_name in printers:
            self.selected_printer= printers[printer_name]
        else:
            raise Exception(f"Error: {printer_name} is not a printer")
        return self.selected_printer
        
    def register_and_run_printers(self):
        results_printers = []
        for compilation_unit in self.compilation_units.values():
            compilation_unit.register_printer(self.selected_printer)
            result= compilation_unit.run_printers()
            printer_results = [x for x in result if x]  # remove empty results
            results_printers.extend(printer_results)
    
    def convert_dot_to_png(self):
        dot = f"call-graph.dot" 
        graph = graphviz.Source.from_file(dot)
        graph.render(filename=dot[:-4], format='png', cleanup=True)
        

class ContractAnalysis:
    def __init__(self, compilation_units :"SafeDevAnalyzer"):
        self.compilation_units = compilation_units
        self.contract_list = self.get_contract_list()
        

instance = RunPrinter("reentrancy.sol")
instance.choose_printer('call-graph')
instance.register_and_run_printers()
instance.convert_dot_to_png()