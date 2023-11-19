from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer   
from slither_core.printers import all_printers
from slither_core.printers.abstract_printer import AbstractPrinter
import inspect
import graphviz
import os
from slither_core.utils.function import get_function_id


# class RunPrinter(SafeDevAnalyzer):
#     def __init__(self, input_file):
#         super().__init__(input_file)
#         self.printer_list = self.get_all_printers()
#         self.selected_printer = ""
#         self.filename = os.path.basename(input_file)[:-4]
        
#     def get_all_printers(self):
#         printers_ = [getattr(all_printers, name) for name in dir(all_printers)]
#         printers = [p for p in printers_ if inspect.isclass(p) and issubclass(p, AbstractPrinter)]
#         return printers

#     def choose_printer(self, printer_name):
#         printers = {p.ARGUMENT: p for p in self.printer_list}
#         if printer_name in printers:
#             self.selected_printer= printers[printer_name]
#         else:
#             raise Exception(f"Error: {printer_name} is not a printer")
#         return self.selected_printer
        
#     def register_and_run_printers(self):
#         results_printers = []
#         for compilation_unit in self.compilation_units.values():
#             compilation_unit.register_printer(self.selected_printer)
#             result= compilation_unit.run_printers()
#             printer_results = [x for x in result if x]  # remove empty results
#             results_printers.extend(printer_results)
    
#     def convert_dot_to_png(self):
#         dot = f"call-graph.dot" 
#         graph = graphviz.Source.from_file(dot)
#         graph.render(filename=dot[:-4], format='png', cleanup=True)
        

def contract_analysis(safe_dev_analyzer: "SafeDevAnalyzer"):
    results= []
    for compilation_unit in safe_dev_analyzer.compilation_units.values():
        for contract in compilation_unit.contracts:
            combined_data={}
            (name, inheritance, _, func_summaries, _) = contract.get_summary()
                
            combined_data["Contract Name"]=name
            combined_data["Inheritance"]=inheritance
            combined_data["State Variables"]={}
            combined_data["State Variables"]["Name"]=[x.name for x in contract.state_variables]
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
                
            for function, state_variable in zip(contract.functions, contract.state_variables_ordered):
                if function.is_shadowed or function.is_constructor_variables:
                    continue
                if not state_variable.is_constant and not state_variable.is_immutable:
                    slot, offset = contract.compilation_unit.storage_layout_of(contract, state_variable)
                    combined_data["State Variables"]["Slot"] = slot
                    combined_data["State Variables"]["Offset"] = offset
        
            for variable in contract.state_variables:
                if variable.visibility in ["public"]:
                    sig = variable.solidity_signature
                    function_id = get_function_id(sig)
                    combined_data["State Variables"]["Name"] = sig
                    combined_data["State Variables"]["Signature"] = f"{function_id:#0{10}x}"

            results.append(combined_data)
            
    return results
        
        

# instance = RunPrinter("reentrancy.sol")
# instance.choose_printer('call-graph')
# instance.register_and_run_printers()
# instance.convert_dot_to_png()
