import os
import cv2
import uuid
import shutil
import easyocr
from os import path
from typing import List, Any, Tuple
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http import models
from time import time
import pandas as pd
import numpy as np
import re
import numpy as np
from numpy import dot
from numpy.linalg import norm


reader = easyocr.Reader(['ko','en'])

encoder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2',device='mps')

search_score = 0.8
width_shrink_ratio = 0.95
height_shrink_ratio = 0.7

def download_file(stream, url):
    if path.exists('images'):
        shutil.rmtree('images')
    os.makedirs('images')

    title = 'video_file' + '.'+ stream.subtype
    stream.download(filename=title)

    if 'DESKTOP_SESSION' not in os.environ:
        with open(title, 'rb') as f:
            try :
                start = time()
                parse_video(url, title)
                print(f"[INFO] Embedding Time {time() - start}")
            except Exception as e :
                print(f"{e}")

        os.remove(title)

def parse_video(file_path: str, encoder, client):
    '''
    이미지 내 텍스트들 OCR 후 중복된 텍스트는 제외하고 Qdrant 에 저장.

    Input
        file_path: 다운로드 한 비디오 파일명
    '''
    init_vector_collection(client)
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"파일 '{file_path}'을(를) 열 수 없습니다.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"파일: {file_path}")
    print(f"FPS: {fps}, 총 프레임 수: {total_frames}, 해상도: {width}x{height}")

    video_area = width * height
    large_area = video_area // 17  # 메인 자막이 차지하는 영역 크기
    frame_count = -1

    color = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 255, 255), (100, 0, 0), (0, 100, 0), (0, 0, 100), (100, 100, 0), (0, 100, 100), (100, 100, 100)]

    while True:
        ret, img = cap.read()
        frame_count += 1

        if int(frame_count % fps) != 0:
            continue

        if ret:
            height, width = img.shape[:2]
            scale_width = width / 1920
            scale_height = height / 1080
            # 기준 포인트를 입력 이미지의 해상도 비율에 맞춰 동적으로 조정
            start_point = (int(1660 * scale_width), int(65 * scale_height))
            end_point = (int(1870 * scale_width), int(155 * scale_height))

            img = cv2.resize(img, (0, 0), fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
            print("이후",img.shape)
            img[start_point[1]*6:end_point[1]*6, start_point[0]*6:end_point[0]*6] = [0, 0, 0]
            cv2.imwrite(f'images6/{str(int(frame_count // fps))}.png', img)
            results = reader.readtext(img)


            if results:
                print(f"프레임 {frame_count // fps}에서 텍스트 감지됨.")
            else:
                print(f"프레임 {frame_count // fps}에서 텍스트 없음.")
                continue

            grouped_boxes = group_similar_boxes(results)

            embeddings = []
            large_list = []
            texts = []

            for idx, val in enumerate(grouped_boxes):
                merged = merge_boxes(val)
                merged_text = remove_special_characters(merged[1])

                for j in val:
                    # color 리스트의 길이를 초과하지 않도록 수정
                    draw_merged_box(img, j, color[idx % len(color)])

                embedding = encoder.encode(merged_text)
                embeddings.append(embedding)
                texts.append(merged_text)
                if merged[2] > large_area:
                    large_list.append(idx)

            search = search_batch_query("OCR", embeddings, 1,client)

            is_save = False
            for idx, val in enumerate(search):
                if len(texts[idx]) < 5: continue
                # search 결과의 안전한 접근을 위한 수정
                if not val or (val and val[0].score < search_score):
                    payload = {'file_path': file_path, 'text': texts[idx], 'time': frame_count // fps}
                    upload_qdrant(payload, [embeddings[idx]], client)

                    if val and idx in large_list:
                        is_save = True

            if is_save:
                cv2.imwrite(f'images/{str(int(frame_count // fps))}.png', img)
        else:
            break


def upload_qdrant(payload: dict, embeddings: List, client):
    id = uuid.uuid4().hex

    client.upsert(
        collection_name="OCR",
        wait=True,
        points=[PointStruct(
            id=id,
            vector=i,
            payload=payload
        ) for i in embeddings]
    )
    return id

def init_vector_collection(client):
    try:
        client.delete_collection("OCR",timeout=1)
    except Exception as e:
        print(f"Qdrant docker delete Exception - {e}")
    try :
        client.create_collection("OCR",vectors_config=VectorParams(size=768, distance=Distance.COSINE))
    except Exception as e:
        print(f"Qdrant docker create Exception - {e}")

def search_batch_query(collection, search_embeddings ,max_results,client):
    """ Search API with query """

    search_queries = []
    collection_name = f"{collection}"
    for i in search_embeddings:
        search_queries.append(
            models.SearchRequest(
                vector=i,
                limit=max_results,
                with_payload=True
            )
        )

    return client.search_batch(collection_name=collection_name, requests=search_queries)

def draw_merged_box(image, merged_box, color):
    coordinates, _, _ = merged_box

    # 원본 bounding box의 좌표 추출
    original_pts = [[int(x), int(y)] for x, y in coordinates]
    original_pts = np.array(original_pts, np.int32)
    original_pts = original_pts.reshape((-1, 1, 2))

    # 축소된 bounding box의 좌표 계산
    min_x_shrink = coordinates[0][0] + (coordinates[1][0] - coordinates[0][0]) * (1 - width_shrink_ratio) / 2
    min_y_shrink = coordinates[0][1] + (coordinates[2][1] - coordinates[0][1]) * (1 - height_shrink_ratio) / 2
    max_x_shrink = coordinates[2][0] - (coordinates[1][0] - coordinates[0][0]) * (1 - width_shrink_ratio) / 2
    max_y_shrink = coordinates[2][1] - (coordinates[2][1] - coordinates[0][1]) * (1 - height_shrink_ratio) / 2

    # 축소된 bounding box의 좌표 계산
    shrink_pts = [
        [int(min_x_shrink), int(min_y_shrink)],
        [int(max_x_shrink), int(min_y_shrink)],
        [int(max_x_shrink), int(max_y_shrink)],
        [int(min_x_shrink), int(max_y_shrink)]
    ]
    shrink_pts = np.array(shrink_pts, np.int32)
    shrink_pts = shrink_pts.reshape((-1, 1, 2))

    # 축소된 bounding box 그리기
    cv2.polylines(image, [shrink_pts], isClosed=True, color=color, thickness=2)

def merge_boxes(group) -> Tuple:
    '''
    같은 그룹에 있는 box 를 합쳐서 좌표와 텍스트, 텍스트 영역 크기 반환
    Bounding box 를 일정 비율로 축소
    Input
        group (List) : OCR 결과인 좌상단 x,y 와 우하단 x,y 가 있는 같은 영역 텍스트들 List
    Output
        (Tuple)
        (
            coordinate (List) : 합쳐진 박스의 좌표
            text (str) : 합쳐진 텍스트
            area (float) : 텍스트의 영역 크기
        )
    '''
    min_x = min(min(x for x, _ in box[0]) for box in group)
    min_y = min(min(y for _, y in box[0]) for box in group)
    max_x = max(max(x for x, _ in box[0]) for box in group)
    max_y = max(max(y for _, y in box[0]) for box in group)

    text = ' '.join([box[1] for box in group])
    area = (max_x - min_x) * (max_y - min_y)

    merged_box = ([[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]], text, area)

    return merged_box

def shrink_coordinates(coordinates):
    ''' Bounding box 사이즈 줄이기 '''
    min_x = min(x for x, _ in coordinates)
    min_y = min(y for _, y in coordinates)
    max_x = max(x for x, _ in coordinates)
    max_y = max(y for x, y in coordinates)

    # 축소된 bounding box의 좌표 계산
    min_x_shrink = min_x + (max_x - min_x) * (1 - width_shrink_ratio) / 2
    min_y_shrink = min_y + (max_y - min_y) * (1 - height_shrink_ratio) / 2
    max_x_shrink = max_x - (max_x - min_x) * (1 - width_shrink_ratio) / 2
    max_y_shrink = max_y - (max_y - min_y) * (1 - height_shrink_ratio) / 2

    return [[min_x_shrink, min_y_shrink], [max_x_shrink, min_y_shrink], [max_x_shrink, max_y_shrink], [min_x_shrink, max_y_shrink]]

def distance_between_boxes(box1, box2):
    ''' 두 Bounding box 의 상하좌우 끝 을 기준으로 거리 계산 '''
    box1 = shrink_coordinates(box1)
    box2 = shrink_coordinates(box2)

    x1_min = min(x for x, _ in box1)
    y1_min = min(y for _, y in box1)
    x1_max = max(x for x, _ in box1)
    y1_max = max(y for _, y in box1)

    x2_min = min(x for x, _ in box2)
    y2_min = min(y for _, y in box2)
    x2_max = max(x for x, _ in box2)
    y2_max = max(y for _, y in box2)

    # 두 박스 중 어느 쪽이 왼쪽에 있는지, 위에 있는지 판단
    left_box = None
    right_box = None
    top_box = None
    bottom_box = None

    if x1_min < x2_min:
        left_box = box1
        right_box = box2
    else:
        left_box = box2
        right_box = box1

    if y1_min < y2_min:
        top_box = box1
        bottom_box = box2
    else:
        top_box = box2
        bottom_box = box1

    left_start = left_box[0]
    left_end = left_box[1]
    right_end = right_box[0]
    top_end = top_box[3]
    bottom_end = bottom_box[0]

    # 거리 계산
    left_distance = abs(left_start[0] - right_end[0])
    left_right_distance = right_end[0] - left_end[0]
    top_bottom_distance = bottom_end[1] - top_end[1]
    top_distance = bottom_end[1] - top_box[0][1]

    return left_distance, left_right_distance, top_bottom_distance, top_distance

def group_similar_boxes(boxes, threshold=100):
    ''' OCR 결과에서 같은 자막끼리 Group '''
    groups = []
    for i, box1 in enumerate(boxes):
        group_found = False
        for group in groups:
            text_group = []
            for box2 in group:
                left_distance, left_right_distance, top_bottom_distance, top_distance = distance_between_boxes(box1[0], box2[0])
                # 가로 조건과 세로 조건을 따로
                if (left_right_distance >= 0 and left_right_distance <= 600 and top_distance <= 10) or \
                    (left_distance <= 25 and top_bottom_distance <= 10):
                    group.append(box1)
                    group_found = True
                    break
            if group_found:
                break
        if not group_found:
            groups.append([box1])

    return groups

def remove_special_characters(input_string):
    ''' 정규 표현식을 사용하여 특수문자를 제외한 문자열을 반환 '''
    return re.sub(r'[^a-zA-Z0-9가-힣\s]', '', input_string)

def cosine_similarity(A, B):
    return dot(A, B)/(norm(A)*norm(B))

def euclidean_distance(A, B):
    return np.sqrt(np.sum((A-B)**2))

def jaccard_similarity(listA, listB):
    s1 = set(listA)
    s2 = set(listB)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))
