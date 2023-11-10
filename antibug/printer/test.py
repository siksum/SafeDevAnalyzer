from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer

target = 'test/enum.sol'
instance = SafeDevAnalyzer(target)

### contract name
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         if contract.is_interface:
#             print("interface contract: ", contract.name)
#         elif contract.is_library:
#             print("library contract: ", contract.name)
#         else:
#             print("general contract: ", contract.name)
#         print(contract.file_scope)

### about structure
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         if contract.structures:
#             for structure in contract.structures:
#                 print("structure name:", structure.name)
#         if contract.structures_inherited:
#             for structure in contract.structures_inherited:
#                 print("inherited structure name:", structure.name)
#         elif contract.structures_declared:
#             for structure in contract.structures_declared:
#                 print("declared structure name:", structure.name)
#                 print(structure.canonical_name)
#                 print(structure.elems)
#                 print(structure.elems_ordered)

### about enum
for compilation_unit in instance.compilation_units.values():
    for contract in compilation_unit.contracts_derived:
        if contract.enums_inherited:
            for enum in contract.enums_inherited:
                print("inherited enum name:", enum.name)
        elif contract.enums_declared:
            for enum in contract.enums_declared:
                print("declared enum name:", enum.name)
                print(enum.canonical_name)
                print(enum.values)
                print(enum.min)
                print(enum.max)
        else:
            for enum in contract.enums:
                print("enum name:", enum.name)  
            