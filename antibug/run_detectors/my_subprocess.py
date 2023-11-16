import subprocess

# 파이썬 서브프로세스 시작
process = subprocess.Popen(
    ['python3', '-u'],  # '-u'는 unbuffered 모드로 실행하도록 지정합니다.
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True  # 텍스트 모드로 설정 (Python 3.5 이상)
)

# 파이썬 서브프로세스와 상호작용
while True:
    user_input = input("Enter Python code (or 'exit' to quit): ")
    
    if user_input == 'exit':
        break
    
    # 사용자 입력을 서브프로세스의 표준 입력으로 전달
    process.stdin.write(user_input + '\n')
    process.stdin.flush()
    
    # 서브프로세스에서의 출력을 읽기
    output = process.stdout.readline()
    error_output = process.stderr.readline()
    
    # 출력 표시
    print("Output:")
    print(output)
    print("Errors:")
    print(error_output)

# 서브프로세스 종료
process.terminate()
