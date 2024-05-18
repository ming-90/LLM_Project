import json

def filter_json_and_save(input_file_name, output_file_name):
    # Load JSON data from the input file
    with open(input_file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Filter out articles with titles containing any of the specified keywords
    keywords = ["하단", "주요뉴스", "CG"]
    filtered_data = {
        "script": [article for article in data['script'] if not any(keyword in article['title'] for keyword in keywords)]
    }

    # Save the filtered data to a new JSON file
    with open(output_file_name, 'w', encoding='utf-8') as file:
        json.dump(filtered_data, file, ensure_ascii=False, indent=4)

# Replace 'input_file_name' and 'output_file_name' with your actual file paths
input_file_name = "mbc_straight.json"
output_file_name = "mbc_straight_refine.json"

filter_json_and_save(input_file_name, output_file_name)
