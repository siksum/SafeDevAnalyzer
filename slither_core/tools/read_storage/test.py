from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer
from slither_core.tools.read_storage.read_storage import SlitherReadStorage
instance = SafeDevAnalyzer('storage.sol')
deployed_address ="0x358AA13c52544ECCEF6B0ADD0f801012ADAD5eE3"
variable_name = "password"

storage = ""
for compilation in instance.compilation_units.values():
    print(compilation.contracts[0])
    storage = SlitherReadStorage(compilation.contracts, 20, None)

storage.get_all_storage_variables(lambda x: x.name == variable_name)
# storage.get_target_variables()
