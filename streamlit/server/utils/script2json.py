import argparse
from PyPDF2 import PdfReader
import json
import re
import os
from kiwipiepy import Kiwi

kiwi = Kiwi()

def remove_all_special_characters(text):
    patterns = [r'◀.*?▶', r'\(.*?\)',r'\[.*?\]']
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    return text

def clean_text_based_on_condition(text):
    # Check if the text starts with the specific sequence of numbers
    if re.match(r'^\d{2}\. \d{1,2}\. \d{1,2}\.', text):
        # Perform the removal only if it starts with the specified pattern
        pattern = r'^\d{2}\. \d{1,2}\. \d{1,2}\..+?\d+/[0-9]{2}'
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
        return cleaned_text
    else:
        # If the text does not start with the specified sequence, return the original text unchanged
        return text

def extract_titles_and_pages(reader):
    pages = reader.pages
    page_list = []
    titles = []

    for page in pages:
        sub = page.extract_text()
        sub = clean_text_based_on_condition(sub)
        page_list.append(sub)

    for page in page_list:
        newline_index = page.find('\n')
        if newline_index != -1:
            substring_before_newline = page[:newline_index]
        else:
            substring_before_newline = page
        if substring_before_newline not in titles:
            titles.append(substring_before_newline)

    return page_list, titles

def process_pages(page_list):
    edit_pages = []

    for page in page_list:
        if page.count("\n") < 4:
            continue
        page = remove_all_special_characters(page)
        edit_pages.append(page)

    pages_with_dates = []
    for page in edit_pages:
        texts = page.split("\n")
        del_text = "\n".join(texts[1:4])
        date = texts[3].replace(" ","")[5:15]
        text = page.replace(del_text, "")
        pages_with_dates.append((text, date))

    return pages_with_dates

def convert_to_json(pages_with_dates):
    content_dict = {}
    for text, date in pages_with_dates:
        first_newline_index = text.find('\n')
        if first_newline_index != -1:
            title = text[:first_newline_index]
            content = text[first_newline_index+1:].replace("\n", "")
        else:
            title = text
            content = ''

        # 동일한 제목이 이미 존재한다면, 내용을 연결합니다.
        if title in content_dict:
            content_dict[title]["content"] += content
        else:
            content_dict[title] = {"title": title, "content": content, "date": date}

    for script in content_dict.values():
        script["content"] = script["content"].replace("  ", " ")
        sentences = kiwi.split_into_sents(script["content"])
        script["content"] = [sentence.text for sentence in sentences]

    # 딕셔너리를 리스트로 변환하여 반환합니다.
    script_list = list(content_dict.values())
    return {"script": script_list}

def process_pdf_file(pdf_path):
    reader = PdfReader(pdf_path)
    page_list, titles = extract_titles_and_pages(reader)
    pages_with_dates = process_pages(page_list)
    script_json = convert_to_json(pages_with_dates)
    return script_json, titles

def process_all_pdfs_in_directory(directory_path):
    all_scripts = []
    all_titles = []
    directory_path = directory_path.strip()
    file_list = os.listdir(directory_path)
    file_list.sort()
    for filename in file_list:
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            script_json, titles = process_pdf_file(pdf_path)
            all_scripts.extend(script_json['script'])
            all_titles.extend(titles)

    return {"script": all_scripts}, all_titles

def process_main(directory_path):
    # print(directory_path)
    combined_script_json, all_titles = process_all_pdfs_in_directory(directory_path)
    json_name = directory_path.split("/")[-1]
    json_name = json_name.strip()
    output_path = os.path.join('output', json_name + '.json')
    # print(json_name)
    if not os.path.exists('./output'):
        os.makedirs('./output')
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(combined_script_json, file, ensure_ascii=False, indent=2)

    with open('output/titles.txt', 'w', encoding='utf-8') as file:
        for title in all_titles:
            file.write(title + "\n")

    print("모든 PDF 파일이 처리되어 JSON 파일과 titles 텍스트 파일이 성공적으로 저장되었습니다.")

    return combined_script_json
