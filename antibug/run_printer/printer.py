from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer   
from slither_core.printers import all_printers
from slither_core.printers.abstract_printer import AbstractPrinter
import inspect
import graphviz
import os
from slither_core.utils.function import get_function_id
from antibug.utils.convert_to_json import get_root_dir

class RunPrinter():
    def __init__(self, safe_dev_analyzer: "SafeDevAnalyzer", printer_name: str):
        self.printer_list = self.get_all_printers()
        self.selected_printer = self.choose_printer(printer_name)
        self.safe_dev_analyzer = safe_dev_analyzer
        
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
        for compilation_unit in self.safe_dev_analyzer.compilation_units.values():
            compilation_unit.register_printer(self.selected_printer)
            compilation_unit.run_printers()
            # printer_results = [x for x in result if x]  # remove empty results
            # results_printers.extend(printer_results)
            
        # return results_printers
    
    # def convert_dot_to_png(self):
    #     dot = f"call-graph.dot"
    #     output_dir_path = os.path.join(get_root_dir(), f"result/call_graph_results/{dot}")
    #     graph = graphviz.Source.from_file(output_dir_path)
    #     graph.render(filename=output_dir_path[:-4], format='png', cleanup=True)
        

def contract_analysis(safe_dev_analyzer: "SafeDevAnalyzer"):
    results= []
    for compilation_unit in safe_dev_analyzer.compilation_units.values():
        for contract in compilation_unit.contracts:
            combined_data={}
            (name, inheritance, _, func_summaries, _) = contract.get_summary()
                
            combined_data["Contract Name"]=name
            combined_data["Inheritance"]=inheritance
            combined_data["State Variables"]={}
            combined_data["State Variables"]={}
            combined_data["Function Summaries"]={}
            
            for function_summary in func_summaries:
                function_name= function_summary[1]
                function_visibility = function_summary[2]
                if function_visibility in ["public", "external"]:
                    function_id = get_function_id(function_name)
                function_modifier = function_summary[3]
                function_internal_calls = function_summary[6]
                function_external_calls = function_summary[7]
                combined_data["Function Summaries"][function_name]={
                    "Name": function_name,
                    "Signature": f"{function_id:#0{10}x}",
                    "Visibility": function_visibility,
                    "Modifiers": function_modifier,
                    "Internal Calls": function_internal_calls,
                    "External Calls": function_external_calls
                }
       
            for variable in contract.state_variables:
                if variable.visibility in ["public"]:
                    sig = variable.solidity_signature
                    function_id = get_function_id(sig)
                    slot, offset = contract.compilation_unit.storage_layout_of(contract, variable)
                    
                    combined_data["State Variables"][sig] ={
                        "Name": variable.name,
                        "Signature": f"{function_id:#0{10}x}",
                        "Slot": slot,
                        "Offset": offset
                    }


            results.append(combined_data)
            
    return results
        
        

# instance = RunPrinter("reentrancy.sol")
# instance.choose_printer('call-graph')
# instance.register_and_run_printers()
# instance.convert_dot_to_png()
