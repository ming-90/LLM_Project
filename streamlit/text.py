import json

# JSON 파일 열기
with open('./brazil.json', 'r') as file:
    data = json.load(file)

# 모든 직원의 이름 추출
names = [script['text'] for script in data['script']['content']]
result = ""

for name in names:
    result += name +" "

print(result)
