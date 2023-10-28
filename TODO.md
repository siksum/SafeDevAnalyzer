# 2023.10.23 (월)

### solc-parser에서 버그 발견

```python
def get_highest_version(self, version_list, target_version, target_index):
    matching_versions = []
    target_major_minor = '.'.join(target_version.split('.')[:2])
    for v in version_list:
        if v.startswith(target_major_minor):
            matching_versions.append(v)
    else:
        return matching_versions[target_index -1]
```

- 기존에는 최신 버전순으로 리스트가 만들어져, 기호에 따라 더 높은 버전을 선택해야 한다면 리스트의 앞 index를 선택하도록 되어있음

  - 잘못 생각했던 부분: ~0.7.6 이면 0.8.0을 골라야 하는 줄 알았음. 생각해보면 0.4버전을 0.8로 실행할 수는 없음. 0.7.6 처럼 마이너 버전의 가장 높은 패치 버전일 경우 그 버전 그대로 선택해야 함. 0.8.0 으로 넘어가면 컴파일이 안됨

- Solution
  ```python
  def get_highest_version(self, version_list, target_version, target_index):
      matching_versions = []
      target_major_minor = '.'.join(target_version.split('.')[:2])
      for v in version_list:
          if v.startswith(target_major_minor):
              matching_versions.append(v)
      if target_version == matching_versions[0]:
          return version_list[target_index]
      else:
          return matching_versions[target_index -1]
  ```
  -

# 2023.10.24 (화)

- c

# 2023.10.25 (수)

### slither wrapping

- slither에서 detector 돌리기 전에 거치는 과정 : Slither -> CryticCompile -> CompilationUnit -> SourceUnit
  - 이때, 버전에 대한 자동화 부분이 존재하지 않음
  - 돌릴때 마다 사용자가 설정해야 하는 문제 발생
  - 만약, 디렉토리 경로를 주고 안에 있는 sol 파일 버전들이 모두 다르다면 돌아가지 않음
- SafeDevAnalyzer wrapping 하여 버전 자동화 및 deploy를 위해 필요한 정보(abi, evm bytecode)를 뽑아내는 클래스 생성

# 2023.10.26 (목)

### SafeDevAnalyzer 폴더 밖에서 sol 파일을 target으로 주면 deploy 결과를 받아올 수 없는 문제 발생

- 기존 코드

  ```python
    def get_root_dir():
        current_working_directory = os.getcwd()
        while not os.path.basename(current_working_directory) == "safe_dev_analyzer":
            current_working_directory = os.path.dirname(current_working_directory)
        return current_working_directory
  ```

  - 디렉토리명을 대문자로 두고, 파일 이름과 디렉토리 이름이 같을 경우 not a package? 그런 에러가 출력됨
  - 그래서 SafeDevAnalyzer를 safe_dev_analyzer로 설정하고 해당 디렉토리를 찾고자 했음
  - get_root_dir 로직 때문에 SafeDevAnalyzer 폴더 밖에서 sol 파일을 target으로 주면 deploy 결과를 받아올 수 없는 문제 발생했음
    ```shell
        $ antibug deploy [target]
    ```

- Solution
  ```python
  def get_root_dir():
      current_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
      return current_path
  ```

<br></br>

### blacklist 기반 detector 붙이기
- slither-simil에 있는 기능 수정하여 lending 관련 취약점 코드를 모아둔 `SafeDevAnalyzer/antibug/run_detectors/based_blacklist/lending` 기반으로 코드 유사도 돌리는 기능 추가
- encode.py에 있는 Slither 클래스 대신 우리가 만들어둔 SafeDevAnalyzer wrapping
  ```python
  def encode_ir(ir):  
      ...
    if isinstance(ir, Index):
        return f"index({ntype(ir.variable_left.type)})"
  
  ```

- 기존에는 Slither 클래스를 호출하고 있어 contract에 바로 접근할 수 있었으나, SafeDevAnalyzer 클래스를 호출할 경우 compilation_unit부터 시작해 contract까지 접근하도록 로직 변경이 필요함
  ```python
  def encode_contract(cfilename, **kwargs):
      r = {}

      # Init slither
      try:
          slither = SafeDevAnalyzer(cfilename, **kwargs)
      except Exception:  # pylint: disable=broad-except
          simil_logger.error("Compilation failed for %s using %s", cfilename, kwargs["solc"])
          return r

      # Iterate over all the contracts
      for compilation_unit in slither.compilation_units.values():
          for contract in compilation_unit.contracts:
              for function in contract.functions_declared:
                  if function.nodes == [] or function.is_constructor_variables:
                      continue

                  x = (cfilename, contract.name, function.name)

                  r[x] = []

                  # Iterate over the nodes of the function
                  for node in function.nodes:
                      # Print the Solidity expression of the nodes
                      # And the SlithIR operations
                      if node.expression:
                          for ir in node.irs:
                              r[x].append(encode_ir(ir))
      return r
  ```
<br></br>

### deploy, detector(basic, blacklist) output JSON으로 뽑아내기
  - result 폴더 내 `deploy_info_json_results`, `basic_detector_json_results`, `blacklist_json_results` 하위에 위치하도록 설정
  - `__main__.py` 내에 로직 수정 -> 리팩토링 필요(다른 파일로 빼는게 좋을 것 같음요)

<br></br>


# TODOs

- [ ] openzepplin import 시 compile이 되지 않는 문제 -> flat으로 해결?

- 해결책 모색 필요함
  <br></br>

- [ ] OPCODE로 코드 가스비 알아내기

- json_result로 보여줄 수 있게
  <br></br>

- [ ] json_result path 바꿀 수 있는 옵션 제공하기

- 현재는 SafeDevAnalyzer/json_result로 생성됨
  
- [ ] detector basic 돌렸을 때 filename, contract, function 추출 시 인덱스 번호가 달라서 추출되지 않는 파일도 존재함
  - test/reentrancy.sol 기준으로 정해둔거라 일반화된 수정 필요함