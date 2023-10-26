# 2023.10.25 (수)



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
<br></br>


# TODOs
[ ] openzepplin import 시 compile이 되지 않는 문제 -> flat으로 해결? 
- 해결책 모색 필요함
<br></br>

[ ] OPCODE로 코드 가스비 알아내기
- json_result로 보여줄 수 있게
<br></br>

[ ] json_result path 바꿀 수 있는 옵션 제공하기
- 현재는 SafeDevAnalyzer/json_result로 생성됨
  