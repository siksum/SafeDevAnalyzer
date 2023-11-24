"""
    Module printing the call graph

    The call graph shows for each function,
    what are the contracts/functions called.
    The output is a dot file named filename.dot
"""
from collections import defaultdict
import os
from typing import Optional, Union, Dict, Set, Tuple, Sequence, List

from slither_core.core.declarations import Contract, FunctionContract
from slither_core.core.declarations.function import Function
from slither_core.core.declarations.solidity_variables import SolidityFunction
from slither_core.core.variables.variable import Variable
from slither_core.printers.abstract_printer import AbstractPrinter
from slither_core.utils.output import Output
from antibug.utils.convert_to_json import output_dir

internal_call_list = []

# return unique id for contract function to use as node name
def _function_node(contract: Contract, function: Union[Function, Variable]) -> str:
    return f"{function.name}"

def _contract_node(function: Union[Function, Variable]) -> str:
    return f"{function.canonical_name.split('.')[0]}"

# return unique id for solidity function to use as node name
def _solidity_function_node(solidity_function: SolidityFunction) -> str:
    return f"{solidity_function.name}"


# return dot language string to add graph edge
def _edge(from_contract: str, to_contract: str) -> str:
    return f'{from_contract} --|> {to_contract}'


# return dot language string to add graph node (with optional label)
def _node(node: str, label: Optional[str] = None) -> str:
    return " ".join(
        (
            f'{label}' if label is not None else "",
        )
    )


# pylint: disable=too-many-arguments
def _process_internal_call(
    contract: Contract,
    function: Function,
    internal_call: Union[Function, SolidityFunction],
    contract_calls: Dict[Contract, Set[str]],
    solidity_functions: Set[str],
    solidity_calls: Set[str],
) -> None:
    if isinstance(internal_call, (Function)):
        contract_calls[contract].add(
            _edge(
                _contract_node(function),
                _contract_node(internal_call),
            )
        )
    elif isinstance(internal_call, (SolidityFunction)):
        solidity_functions.add(
            _node(_solidity_function_node(internal_call)),
        )
        # solidity_calls.add(
        #     _edge(
        #         _function_node(contract, function),
        #         _solidity_function_node(internal_call),
        #     )
        # )
        internal_call_list.append(internal_call)
    return contract_calls[contract]


def _render_external_calls(external_calls: Set[str]) -> str:
    return "\n".join(external_calls)


def _render_internal_calls(
    contract: Contract,
    contract_functions: Dict[Contract, Set[str]],
    contract_calls: Dict[Contract, Set[str]],
) -> str:
    lines = []

    lines.append(f'\tclass {contract.name}{{')
    for temp in contract_functions[contract]:
        lines.append(f'\t\t{temp}')
    # lines.extend(contract_calls[contract])

    lines.append("\t}\n")

    return "\n".join(lines)


def _render_solidity_calls( solidity_calls: Set[str]) -> str:
    lines = []
    lines.append('\tclass Solidity{')
    
    for internal_call in internal_call_list:
        node = _solidity_function_node(internal_call)
        lines.append(f'\t\t{node}')
    lines.append("\t}\n")
        
    lines.extend(solidity_calls)


    return "\n".join(lines)


def _process_external_call(
    contract: Contract,
    function: Function,
    external_call: Tuple[Contract, Union[Function, Variable]],
    contract_functions: Dict[Contract, Set[str]],
    external_calls: Set[str],
    all_contracts: Set[Contract],
) -> None:
    external_contract, external_function = external_call

    if not external_contract in all_contracts:
        return

    # add variable as node to respective contract
    if isinstance(external_function, (Variable)):
        contract_functions[external_contract].add(
            _node(
                _function_node(external_contract, external_function),
                external_function.name,
            )
        )

    external_calls.add(
        _edge(
            _function_node(contract, function),
            _function_node(external_contract, external_function),
        )
    )


# pylint: disable=too-many-arguments
def _process_function(
    contract: Contract,
    function: Function,
    contract_functions: Dict[Contract, Set[str]],
    contract_calls: Dict[Contract, Set[str]],
    solidity_functions: Set[str],
    solidity_calls: Set[str],
    external_calls: Set[str],
    all_contracts: Set[Contract],
) -> None:
    contract_functions[contract].add(
        _node(_function_node(contract, function), function.name),
    )
    contract_edge = set()
    for internal_call in function.internal_calls:
        edge=_process_internal_call(
            contract,
            function,
            internal_call,
            contract_calls,
            solidity_functions,
            solidity_calls,
        )
        contract_edge.update(edge)
        
    for external_call in function.high_level_calls:
        _process_external_call(
            contract,
            function,
            external_call,
            contract_functions,
            external_calls,
            all_contracts,
        )
    return contract_edge

def _process_functions(functions: Sequence[Function]) -> str:
    # TODO  add support for top level function

    contract_functions: Dict[Contract, Set[str]] = defaultdict(
        set
    )  # contract -> contract functions nodes
    contract_calls: Dict[Contract, Set[str]] = defaultdict(set)  # contract -> contract calls edges

    solidity_functions: Set[str] = set()  # solidity function nodes
    solidity_calls: Set[str] = set()  # solidity calls edges
    external_calls: Set[str] = set()  # external calls edges

    all_contracts = set()
    contract_edges = set()
    for function in functions:
        if isinstance(function, FunctionContract):
            all_contracts.add(function.contract_declarer)
    for function in functions:
        if isinstance(function, FunctionContract):
            edge = _process_function(
                function.contract_declarer,
                function,
                contract_functions,
                contract_calls,
                solidity_functions,
                solidity_calls,
                external_calls,
                all_contracts,
            )
            contract_edges.update(edge)

    render_internal_calls = ""
    for contract in all_contracts:
        render_internal_calls += _render_internal_calls(
            contract, contract_functions, contract_calls
        )  
        
    render_solidity_calls = _render_solidity_calls(solidity_calls)
    render_external_calls = _render_external_calls(external_calls)
    
    if render_solidity_calls:
        for contract in all_contracts:
            edge = _edge(f"{contract}", "Solidity\n")
    if contract_edges is not None:
        contract_edge = "\n".join(contract_edges)
    return render_internal_calls + render_solidity_calls + render_external_calls + edge + contract_edge


class PrinterCallGraph(AbstractPrinter):
    ARGUMENT = "call-graph"
    HELP = "Export the call-graph of the contracts to a dot file"

    WIKI = "https://github.com/trailofbits/slither/wiki/Printer-documentation#call-graph"

    def output(self, filename: str) -> Output:
        """
        Output the graph in filename
        Args:
            filename(string)
        """
        output_dir_path =output_dir("call_graph_results")
        os.chmod(output_dir_path, 0o777)
        

        all_contracts_filename = ""
        if not filename.endswith(".html"):
            if filename in ("", "."):
                filename = ""
            else:
                filename += "."
            all_contracts_filename = os.path.join(output_dir_path, f"all_contracts.call-graph.html")

        if filename == ".html":
            all_contracts_filename = os.path.join(output_dir_path, "all_contracts.html")

        info = ""
        results = []
        # with open(all_contracts_filename, "w", encoding="utf8") as f:
        #     info += f"Call Graph: {all_contracts_filename}\n"

        #     # Avoid duplicate functions due to different compilation unit
        #     all_functionss = [
        #         compilation_unit.functions for compilation_unit in self.slither.compilation_units
        #     ]
        #     all_functions = [item for sublist in all_functionss for item in sublist]
        #     all_functions_as_dict = {
        #         function.canonical_name: function for function in all_functions
        #     }
        #     content = "\n".join(
        #         ["classDiagram"]
        #         + [_process_functions(list(all_functions_as_dict.values()))]
        #     )
        #     f.write(content)
        #     results.append((all_contracts_filename, content))   

        for derived_contract in self.slither.contracts_derived:
            derived_output_filename = os.path.join(output_dir_path, f"call-graph.html")
            with open(derived_output_filename, "w", encoding="utf8") as f:
                info += f"Call Graph: {derived_output_filename}\n"
                content = "\n".join(
                    ["<script src='https://unpkg.com/mermaid@8.1.0/dist/mermaid.min.js'></script>"] + ["<div class='mermaid'>"] + ["classDiagram"] + [_process_functions(derived_contract.functions)] + ["</div>"]
                )
                f.write(content)
                results.append((derived_output_filename, content))

        self.info(info)
        res = self.generate_output(info)
        for filename_result, content in results:
            res.add_file(filename_result, content)

        return res
