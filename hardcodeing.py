import uvicorn
import os
from fastapi import FastAPI
from openai import OpenAI
import sys

page = 0

api_key = 'up_6eHwf9HchV62oTWIwTI7jd9e4XcxP'
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")

while True:
    if page == 0:
        print("문제점을 제시 해 주세요.")
        text = sys.stdin.readline()

        system_prompt = '''TRIZ 정보 입력
나는 TRIZ 원리로 문제를 해결하고 싶어 일단 먼저 TRIZ가 무엇인지 설명을 해줄게
TRIZ 는  Theory of solving inventive problem 방법론의 줄임말로 40가지 원리를 가지고 있어. 40가지 원리는 아래와 같아
평형추 (Counterweight)
분할 (Segmentation)
분리 (Extraction)
국소품질 (Local quality)
비대칭 (Asymmetry)
병합 (Merging) - 시간과 공간
범용성 (Universality)
포개기 (Nesting)
사전 예방조처 (Preliminary anti-action)
사전 준비조처 (Prior action)
사전 보호조처 (Beforehand cushioning)
높이 유지 (Equipotentiality)
반전 (Inversion)
타원체 (Spheroidality)
유연성 (Flexibility)
조처 과부족 (Partial or excessive action)
다른 차원 (Another dimension)
기계적 진동 (Mechanical vibration)
주기적 조처 (Periodic action)
유용한 조처의 지속 (Continuity of useful action)
건너뛰기 (Skipping)
유해 물 이용 (Convert harm into benefit)
피드백 (Feedback)
중간 매개물 (Intermediary)
셀프서비스 (Self-service)
대체수단 (Copying)
일회용품 (Cheap short-living objects)
기계식 시스템의 대체 (Replace a mechanical system)
공압 및 수압 (Pneumatics and hydraulics)
연한 껍질이나 얇은 막 (Flexible shells and thin films)
다공성 소재 (Porous materials)
색상변화 (Color changes)
동질성 (Homogeneity)
폐기 또는 복구 (Discarding and recovering)
모수변화 (Parameter changes)
상태전이 (Phase transitions)
열팽창 (Thermal expansion)
강한 산화제의 이용 (Use strong oxidizers)
불활성 환경 (Inert environment)
복합재료 (Composite materials)'''

        system_prompt2 = '''일반화 결과물 양식은 아래와 같아
‘피망을 통조림으로 만들려면 꼬투리와 씨를 제거해야한다. 모양과 크기가 다양한 피망은 기계로 자동화 하기가 매우 어려워 수작업에 의존해왔다’
라는 문제가 제시되었을 때 일반화는
‘어떻게 하면 전체에서 일부분을 분리할 수 있을까?’
일반화의 결과물은 한줄로 요약해서 보내줘'''

        chat_result = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": system_prompt},
        {'role':'user', 'content':text + system_prompt2}
        ])

        result = chat_result.choices[0].message.content
        print("==============================")
        print("결과 입니다. ")
        print(result)
        print("==============================")
        page += 1

    if page == 1:
        system_prompt = '''TRIZ 정보 입력
나는 TRIZ 원리로 문제를 해결하고 싶어 일단 먼저 TRIZ가 무엇인지 설명을 해줄게
TRIZ 는  Theory of solving inventive problem 방법론의 줄임말로 40가지 원리를 가지고 있어. 40가지 원리는 아래와 같아
평형추 (Counterweight)
분할 (Segmentation)
분리 (Extraction)
국소품질 (Local quality)
비대칭 (Asymmetry)
병합 (Merging) - 시간과 공간
범용성 (Universality)
포개기 (Nesting)
사전 예방조처 (Preliminary anti-action)
사전 준비조처 (Prior action)
사전 보호조처 (Beforehand cushioning)
높이 유지 (Equipotentiality)
반전 (Inversion)
타원체 (Spheroidality)
유연성 (Flexibility)
조처 과부족 (Partial or excessive action)
다른 차원 (Another dimension)
기계적 진동 (Mechanical vibration)
주기적 조처 (Periodic action)
유용한 조처의 지속 (Continuity of useful action)
건너뛰기 (Skipping)
유해 물 이용 (Convert harm into benefit)
피드백 (Feedback)
중간 매개물 (Intermediary)
셀프서비스 (Self-service)
대체수단 (Copying)
일회용품 (Cheap short-living objects)
기계식 시스템의 대체 (Replace a mechanical system)
공압 및 수압 (Pneumatics and hydraulics)
연한 껍질이나 얇은 막 (Flexible shells and thin films)
다공성 소재 (Porous materials)
색상변화 (Color changes)
동질성 (Homogeneity)
폐기 또는 복구 (Discarding and recovering)
모수변화 (Parameter changes)
상태전이 (Phase transitions)
열팽창 (Thermal expansion)
강한 산화제의 이용 (Use strong oxidizers)
불활성 환경 (Inert environment)
복합재료 (Composite materials)'''

        system_prompt2 = '''일반화 결과물 양식은 아래와 같아
‘피망을 통조림으로 만들려면 꼬투리와 씨를 제거해야한다. 모양과 크기가 다양한 피망은 기계로 자동화 하기가 매우 어려워 수작업에 의존해왔다’
라는 문제가 제시되었을 때 일반화는
‘어떻게 하면 전체에서 일부분을 분리할 수 있을까?’
일반화의 결과물은 한줄로 요약해서 보내줘'''
        system_prompt3 = '''
        아래 양식에 맞춰서 TRIZ 원리를 적용해서 해결책을 적용해줘
        해결책은 5개만 보여줘

TRIZ 문제 정의
문제 상황 (일반화):
어떻게 하면 특정 대상에서 일부분을 효율적으로 분리할 수 있을까?
기능적 접근
필요한 기능:
분리 기능: 대상에서 일부분을 분리해야 함
효율성 기능: 분리 과정이 효율적이어야 함
이상적 결과 도출
이상적 결과:
{{}}
자원 분석
사용 가능한 자원:
{{}}
TRIZ 40가지 발명 원리 적용
해결 방안 도출
TRIZ 40가지 발명 원리 적용

- 1. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 2. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 3. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 4. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 5. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}
        '''

        chat_result = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": system_prompt},
        {'role':'user', 'content':text + system_prompt2},
        {"role": "system", "content": system_prompt3},
        {'role':'user', 'content':'''기준을 가지고 해결 방안들을 1점부터 7점 척도로 평가를 출력해줘. 점수가 높은 5개만 알려줘'''},
        ])

        result = chat_result.choices[0].message.content

        print("\n")
        print("\n")
        print("\n")
        print("평가 기준으로 해결 방안을 1점부터 7점의 척도로 출력한 결과 입니다. ")
        print(result)

        num1 = result.index('1. 원리')

        if num1 != -1:
            page += 1

    if page == 2:
        print('======================')
        c = int(input())
        system_prompt = '''TRIZ 정보 입력
나는 TRIZ 원리로 문제를 해결하고 싶어 일단 먼저 TRIZ가 무엇인지 설명을 해줄게
TRIZ 는  Theory of solving inventive problem 방법론의 줄임말로 40가지 원리를 가지고 있어. 40가지 원리는 아래와 같아
평형추 (Counterweight)
분할 (Segmentation)
분리 (Extraction)
국소품질 (Local quality)
비대칭 (Asymmetry)
병합 (Merging) - 시간과 공간
범용성 (Universality)
포개기 (Nesting)
사전 예방조처 (Preliminary anti-action)
사전 준비조처 (Prior action)
사전 보호조처 (Beforehand cushioning)
높이 유지 (Equipotentiality)
반전 (Inversion)
타원체 (Spheroidality)
유연성 (Flexibility)
조처 과부족 (Partial or excessive action)
다른 차원 (Another dimension)
기계적 진동 (Mechanical vibration)
주기적 조처 (Periodic action)
유용한 조처의 지속 (Continuity of useful action)
건너뛰기 (Skipping)
유해 물 이용 (Convert harm into benefit)
피드백 (Feedback)
중간 매개물 (Intermediary)
셀프서비스 (Self-service)
대체수단 (Copying)
일회용품 (Cheap short-living objects)
기계식 시스템의 대체 (Replace a mechanical system)
공압 및 수압 (Pneumatics and hydraulics)
연한 껍질이나 얇은 막 (Flexible shells and thin films)
다공성 소재 (Porous materials)
색상변화 (Color changes)
동질성 (Homogeneity)
폐기 또는 복구 (Discarding and recovering)
모수변화 (Parameter changes)
상태전이 (Phase transitions)
열팽창 (Thermal expansion)
강한 산화제의 이용 (Use strong oxidizers)
불활성 환경 (Inert environment)
복합재료 (Composite materials)'''

        system_prompt2 = '''일반화 결과물 양식은 아래와 같아
‘피망을 통조림으로 만들려면 꼬투리와 씨를 제거해야한다. 모양과 크기가 다양한 피망은 기계로 자동화 하기가 매우 어려워 수작업에 의존해왔다’
라는 문제가 제시되었을 때 일반화는
‘어떻게 하면 전체에서 일부분을 분리할 수 있을까?’
일반화의 결과물은 한줄로 요약해서 보내줘'''
        system_prompt3 = '''
        아래 양식에 맞춰서 TRIZ 원리를 적용해서 해결책을 적용해줘
        해결책은 5개만 보여줘

TRIZ 문제 정의
문제 상황 (일반화):
어떻게 하면 특정 대상에서 일부분을 효율적으로 분리할 수 있을까?
기능적 접근
필요한 기능:
분리 기능: 대상에서 일부분을 분리해야 함
효율성 기능: 분리 과정이 효율적이어야 함
이상적 결과 도출
이상적 결과:
{{}}
자원 분석
사용 가능한 자원:
{{}}
TRIZ 40가지 발명 원리 적용
해결 방안 도출
TRIZ 40가지 발명 원리 적용

- 1. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 2. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 3. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 4. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}

- 5. 원리 {{}} : {{}}
- 내용  : {{}}
- 평가 : {{}}
        '''
        chat_result = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": system_prompt},
        {'role':'user', 'content':text + system_prompt2},
        {"role": "system", "content": system_prompt3},
        {'role':'user', 'content':'''기준을 가지고 해결 방안들을 1점부터 7점 척도로 평가를 출력해줘. 점수가 높은 5개만 알려줘'''},
        {'role':'user', 'content':f'해결 방안 {c}번이 좋을 것 같은데, 이것을 내가 제품 개발에 실제로 적용하려면 어떤 과정을 거쳐야 할까?'},
        ])

        result = chat_result.choices[0].message.content

        print(result)

