from typing import List

from slither_core.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither_core.utils.output import Output
from slither_core.slithir.operations import InternalCall, LibraryCall
from collections import Counter

class addLiquidity(AbstractDetector):
    ARGUMENT = "addLiquidity"
    HELP = "logic check in DEX"
    IMPACT = DetectorClassification.LOW
    CONFIDENCE = DetectorClassification.LOW

    WIKI = "https://github.com/Uniswap/v2-periphery/blob/0335e8f7e1bd1e8d8329fd300aea2ef2f36dd19f/contracts/UniswapV2Router01.sol#L58"
    WIKI_TITLE = "logic example"
    WIKI_DESCRIPTION = "logic example"
    WIKI_EXPLOIT_SCENARIO = ".."
    WIKI_RECOMMENDATION = ".."

    def _detect(self) -> List[Output]:
        set1 = []
        set2 = []
        set3 = []
        results = []
        
        for contract in self.compilation_unit.contracts:
            for function in contract.functions:
                if function.visibility in ['external']:
                    for node in function.nodes:
                        for ir in node.irs:
                            if self.has_safeTransfer(ir): set1.append(node.function.name)
                            if self.has_optiomal_calculate(ir): set2.append(node.function.name)
        
        counter = Counter(set1)
        for func, count in counter.items():
            if count == 2:
                set3.append(func)

        matches = set(set3) & set(set2)
        
        for match in matches:
            # results.append(self.generate_result(f"{match}n"))  
            results.append(self.generate_result(f"{match}"))        
        return results

    @staticmethod
    def has_safeTransfer(ir):
        func = []
        if isinstance(ir, LibraryCall):
            if ir.function_name == 'safeTransferFrom':
                return True
                
    @staticmethod
    def has_optiomal_calculate(ir): 
        if isinstance(ir, InternalCall):
            if (len(ir.function.returns) == 2):
                for n in ir.arguments:
                    if str(n) != 'msg.value':
                        return True