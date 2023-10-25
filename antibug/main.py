from antibug.antibug_compile.compile import SafeDevAnalyzer
from Crytic_compile.utils.naming import convert_filename
from pathlib import Path

import sys
import json

def convert_to_json(abi_list, bytecode_list):
    combined_data = {}

    for abi, bytecode in zip(abi_list, bytecode_list):
        # abi와 bytecode의 키(예: 'EtherGame')를 가져옴
        key = next(iter(abi))
        
        # 해당 키에 대한 데이터가 이미 combined_data에 있다면, 데이터를 업데이트
        if key in combined_data:
            combined_data[key]['abis'].extend(abi[key])
            combined_data[key]['bytecodes'] = ("0x"+bytecode[key]) # bytecode는 덮어씌우는 형태로 합니다.
        else:
            combined_data[key] = {
                "abis": abi[key],
                "bytecodes": "0x"+bytecode[key]
            }

    combined_json = json.dumps(combined_data, indent=4)
    open ("abi_bytecode.json", "w").write(combined_json)

if __name__ == "__main__":
    analyzer = SafeDevAnalyzer(sys.argv[1])
    abi_list, bytecode_list = analyzer.to_deploy()
    convert_to_json(abi_list, bytecode_list)
