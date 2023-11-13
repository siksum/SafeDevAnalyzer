from antibug.compile.safe_dev_analyzer import SafeDevAnalyzer

target = 'test/storage.sol'
# target = 'test/reentrancy.sol'
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
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         if contract.enums_inherited:
#             for enum in contract.enums_inherited:
#                 print("inherited enum name:", enum.name)
#         elif contract.enums_declared:
#             for enum in contract.enums_declared:
#                 print("declared enum name:", enum.name)
#                 print(enum.canonical_name)
#                 print(enum.values)
#         else:
#             for enum in contract.enums:
#                 print("enum name:", enum.name)  

### about event
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         if contract.events_inherited:
#             for event in contract.events_inherited:
#                 print("inherited event name:", event)
#         elif contract.events_declared:
#             for event in contract.events_declared:
#                 print("declared event name:", event)
#                 print("signature:",event.signature)
#                 print("full_name:",event.full_name)
#                 print("canonical_name:",event.canonical_name)
#                 print("elms",event.elems)
#                 print("declared by contract",event.is_declared_by(contract))
#         else:
#             for event in contract.events:
#                 print("event name:", event)

### about custom error
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         if contract.custom_errors_inherited:
#             for error in contract.custom_errors_inherited:
#                 print("inherited error name:", error)
#         elif contract.custom_errors_declared:
#             for error in contract.custom_errors_declared:
#                 print("declared error name:", error)
                
#                 ###### CustomErrorContract ######
#                 print("is declared by contract:", error.is_declared_by(contract))
#                 print("canonical name:", error.canonical_name)
                
#                 ###### CustomError ######
#                 print("parameters:", error.parameters)
#                 print("signature", error.solidity_signature)
#                 print("full name:", error.full_name)
#         else:
#             for error in contract.custom_errors:
#                 print("error name:", error)

### about type alias                
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         if contract.type_aliases_inherited:
#             for type_alias in contract.type_aliases_inherited:
#                 print("inherited type alias name:", type_alias)
#         elif contract.type_aliases_declared:
#             for type_alias in contract.type_aliases_declared:
#                 print("declared type alias name:", type_alias)
#                 # print("type:", type_alias.type)
#         else:
#             for type_alias in contract.type_aliases:
#                 print("type alias name:", type_alias)
                

### about type variable
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
        # if contract.state_variables_inherited:
        #     for variable in contract.state_variables_inherited:
        #         print("inherited variable name:", variable.name)
        # elif contract.state_variables_declared:
        #     for variable in contract.state_variables_declared:
        #         print("declared variable name:", variable.name)
                # print("canonical name:", variable.canonical_name)
                # print("full name:", variable.full_name)
                # print(variable.node_initialization)
        #         print(variable.visibility)
        # else:
        #     for variable in contract.state_variables:
        #         print("variable name:", variable.name)
        
    # print(contract.state_variables_used_in_reentrant_targets)
        
### about type constructor     
# for compilation_unit in instance.compilation_units.values():
#     for contract in compilation_unit.contracts_derived:
#         print(contract.constructor)
#         print(contract.constructors_declared)
#         print(contract.constructors)
#         print(contract.explicit_base_constructor_calls)


for compilation_unit in instance.compilation_units.values():
     for contract in compilation_unit.contracts_derived:
         print(contract.get_summary())