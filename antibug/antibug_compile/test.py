from crytic_compile.crytic_compile import CryticCompile
from crytic_compile.compilation_unit import CompilationUnit

from typing import TYPE_CHECKING
from safe_dev_analyzer import SafeDevCompile
import sys
if TYPE_CHECKING:
    
    from compile.compilation_unit import SafeDevCompilationUnit



crytic = CryticCompile(sys.argv[1])
crytic_instance = CompilationUnit(crytic, ".")

print(crytic_instance.asts)

safedev = SafeDevCompile(sys.argv[1])
safedev_instance = SafeDevCompilationUnit(safedev, ".")

print(safedev_instance.asts)

