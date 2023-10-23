

from crytic_compile.compilation_unit import CompilationUnit
from crytic_compile.crytic_compile import CryticCompile

from safe_dev_analyzer import SafeDevCompile
from compilation_unit import SafeDevCompilationUnit
import sys

crytic = CryticCompile(sys.argv[1])
instance = CompilationUnit(crytic, "Aaa")
print(instance.filename_to_contracts)

safe_dev = SafeDevCompile(sys.argv[1])
instance1 = SafeDevCompilationUnit(safe_dev, "baa")
print(safe_dev.compilation_units) 