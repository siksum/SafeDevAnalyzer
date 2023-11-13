import json

data = {
    "description_korean": "inline assembly block에서 return이 사용되어 반환할 수 없는 실행 흐름입니다.",
    "exploit_scenario_korean": "한국어 설명을 추가하세요.",
    "recommendation_korean": "추천 사항을 한국어로 작성하세요."
}

# JSON 문자열로 변환
json_data = json.dumps(data, ensure_ascii=False)
print(json_data)
