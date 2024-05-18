import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance, VectorParams
import uuid

def parse_json_sentence(json_data):
    parsed_data = []
    for article in json_data['script']:
        title = article['title']
        date = article['date']
        for i, text in enumerate(article['content']):
            parsed_data.append({
                "index": i,
                "text": text,
                "title": title,
                "date": date
            })
    return parsed_data

def parse_script_paragraph(json_data):
    parsed_data = []
    for article in json_data['script']:
        title = article['title']
        date = article['date']
        content = " ".join(article['content'])
        parsed_data.append({
            "text": content,
            "title": title,
            "date": date
        })
    return parsed_data

def parse_subtitle_paragraph(json_data):
    parsed_data = []
    for article in json_data['subtitle']:
        title = article['title']
        date = article['date']
        content = " ".join(article['content'])
        parsed_data.append({
            "text": content,
            "title": title,
            "date": date
        })
    return parsed_data

def seconds_to_min_sec(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes}:{seconds:02d}"

def parse_stt(json_data):
    parsed_data = []
    for i, content in enumerate(json_data['script']['content']):
        parsed_data.append({
            "index": i,
            "text": content['text'],
            "start": content['start'],
            "end": content['end']
        })
    return parsed_data

def initialize_qdrant_collection(encoder,client, json_file, collection_name):
    # 컬렉션이 없으면 생성
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=encoder.get_sentence_embedding_dimension(),
            distance=models.Distance.COSINE,
        ),
    )
    if collection_name == "pdf_script":
        parsed_data = parse_script_paragraph(json_file)
        client.upload_records(
        collection_name=collection_name,
        records=[
            models.Record(
                id=idx,
                vector=encoder.encode(doc["text"]).tolist(),
                payload={
                    # "index": doc["index"],
                    "text": doc["text"],
                    "title": doc["title"],
                    "date": doc["date"]
                }
            )
            for idx, doc in enumerate(parsed_data)
        ],
    )
    elif collection_name == "pdf_subtitle":
        parsed_data = parse_subtitle_paragraph(json_file)
        client.upload_records(
        collection_name=collection_name,
        records=[
            models.Record(
                id=idx,
                vector=encoder.encode(doc["text"]).tolist(),
                payload={
                    # "index": doc["index"],
                    "text": doc["text"],
                    "title": doc["title"],
                    "date": doc["date"]
                }
            )
            for idx, doc in enumerate(parsed_data)
        ],
    )
    elif collection_name == "STT":
        parsed_data = parse_stt(json_file)
        client.upload_records(
        collection_name=collection_name,
        records=[
            models.Record(
                id=idx,
                vector=encoder.encode(doc["text"]).tolist(),
                payload={
                    # "index": doc["index"],
                    "text": doc["text"],
                    "start": doc["start"],
                    "end": doc["end"]
                }
            )
            for idx, doc in enumerate(parsed_data)
        ],
    )

    else:
        print("Invalid collection name")
    # parsed_data = parse_json_sentence(json_file)

    # Qdrant에 업로드할 레코드 생성 및 업로드

