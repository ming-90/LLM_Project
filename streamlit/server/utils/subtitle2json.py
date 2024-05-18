import argparse
from PyPDF2 import PdfReader
import json
import re
import os

# 문자열이 숫자로 시작하는지 확인하고, 그렇지 않은 경우 이전 문자열에 병합
def merge_strings_if_not_start_with_number(strings):
    result = []
    for s in strings:
        # 맨 앞 글자가 숫자인지 검사
        if re.match(r'^\d', s):
            # 숫자로 시작하면 현재 문자열을 결과 리스트에 추가
            result.append(s)
        else:
            # 숫자로 시작하지 않으면 마지막 문자열에 현재 문자열을 추가
            if result:
                result[-1] += s
            else:
                # 결과 리스트가 비어있는 경우 현재 문자열을 그대로 추가
                result.append(s)
    return result

# 문자열을 순서대로 번호 매기고, 순서에 맞지 않는 경우 이전 문자열에 병합
def ordered_number(strings):
    result = []
    order_number = 1
    for s in strings:
        # 현재 순서 번호로 시작하고, 그 다음 문자가 비숫자인지 확인
        if re.match(rf'^{order_number}[^0-9]', s):
            result.append(s)
            order_number += 1
        else:
            if result:
                result[-1] += ' ' + s  # 여기서 ' '을 추가하여 문자열을 구분
            else:
                result.append(s)
    return result

def remove_leading_numbers(strings):
    result = []
    order_number = 1
    for s in strings:
        # 현재 순서 번호로 시작하는지 확인하고, 맞으면 해당 숫자만 제거
        if re.match(rf'^{order_number}\D', s):
            new_string = re.sub(rf'^{order_number}', '', s)
            result.append(new_string)
            order_number += 1
        else:
            result.append(s)
    return result

# 중복된 문자열 제거
def remove_duplicate(strings):
    result = []
    for s in strings:
        if s not in result:
            result.append(s)
    return result

def script_title_match(title, script_json_name):
    with open(script_json_name, 'r') as script:
        script_data = json.load(script)

    for data in script_data['script']:
        if title == data['title']:
            return data['date']

# PDF 페이지의 텍스트 추출 및 정제
def process_pdf_file(pdf_file_path, titles, unmatched_titles, script_json_name):
    reader = PdfReader(pdf_file_path)
    pages = reader.pages
    page_list = []
    subtitles = {}
    script_json_name = script_json_name.strip()

    for page in pages:
        sub = page.extract_text()
        page_list.append(sub)

    for page in page_list:
        texts = page.split("\n")

        title_part = texts[2][:-9] # 제목부분 일부를 보고 배치하기 때문에 100% 보장하지 않음
        matched_titles = [title for title in titles if title.startswith(title_part)]

        if matched_titles:
            title = matched_titles[0]
            del_index = texts.index('여부')
            del texts[: del_index + 1]
            del_index = texts.index('여부')
            del texts[: del_index + 1]

            texts = merge_strings_if_not_start_with_number(texts)

            if title in subtitles:
                subtitles[title]['content'].extend(texts)
            else:
                date = script_title_match(title, script_json_name)
                subtitles[title] = {
                    "content": texts,
                    "date": date
                }
        else:
            unmatched_titles.add(title_part)  # 매치되지 않은 제목 추가

    final_list = []

    for title, data in subtitles.items():
        remove_dupl_data = remove_duplicate(data['content'])
        ordered_content = ordered_number(remove_dupl_data)
        remove_leading_numbers_data = remove_leading_numbers(ordered_content)
        final_list.append({
            "title": title,
            "content": remove_leading_numbers_data,
            "date": data['date']
        })

    return final_list

def process_main(directory_path,script_json_name):
    # 타이틀 파일 읽기 및 초기화
    titles = []
    unmatched_titles = set()  # 매치되지 않은 제목들을 저장할 집합
    if not os.path.exists('output'):
        os.makedirs('output')
    with open('output/titles.txt', 'r') as file: # script 프로세스시 만든 txt 참고해야함
        for line in file:
            titles.append(line.strip())

    # 폴더 내의 모든 PDF 파일 처리
    all_subtitles = []
    directory_path = directory_path.strip()
    file_list = os.listdir(directory_path)
    file_list.sort()
    script_json_name = script_json_name.strip() + ".json"
    for filename in file_list:
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            all_subtitles.extend(process_pdf_file(pdf_path, titles, unmatched_titles,script_json_name))

    final_json = {
        "subtitle": all_subtitles
    }
    json_name = directory_path.split("/")[-1]
    json_name = json_name.strip()
    output_path = os.path.join('output', json_name + '.json')
    # JSON 파일 저장
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(final_json, json_file, ensure_ascii=False, indent=4)

    # # 매치되지 않은 제목들을 텍스트 파일로 저장
    # with open('unmatched_titles.txt', 'w', encoding='utf-8') as file:
    #     for title in unmatched_titles:
    #         file.write(title + '\n')

    print("생성한 all_subtitles 개수(리포트 개수임)", len(all_subtitles))
    print("JSON 파일이 성공적으로 저장되었습니다.")

    return final_json