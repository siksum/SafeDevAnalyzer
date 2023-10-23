import uuid
import sys
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Set, Optional


if TYPE_CHECKING:
    from safe_dev_analyzer import SafeDevCompile, Filename

class SafeDevCompilationUnit:
    def __init__(self, safe_dev_compile: "SafeDevCompile", unique_id: str):
        if unique_id == ".":
            unique_id = str(uuid.uuid4())
        self._unique_id = unique_id
        self._safe_dev_compile: "SafeDevCompile" = safe_dev_compile
        
    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def safe_dev_compile(self) -> "SafeDevCompile":
        return self._safe_dev_compile
    
    # @property
    # def source_units(self) -> Dict["Filename"]:
    #     return self._safe_dev_compile.source