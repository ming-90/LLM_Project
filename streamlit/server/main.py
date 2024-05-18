from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from utils import json2qdrant
from utils import script2json, subtitle2json, whisper_x, videoOCR, search
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import tempfile
import time

app = FastAPI()

encoder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
client = QdrantClient(host="localhost", port=6333)

class PdfParseRequest(BaseModel):
    option: str
    dir_path: str
    script_json_name: str

class SearchRequest(BaseModel):
    collection_name: str
    search_text: str

@app.post("/ocr-process")
async def ocr_process(file: UploadFile = File(...)):
    start_time = time.time()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
        content = await file.read()
        tmpfile.write(content)
        video_file_path = tmpfile.name
    videoOCR.parse_video(video_file_path, encoder, client)
    end_time = time.time()  # 실행 종료 시간 기록
    elapsed_time = end_time - start_time  # 경과 시간 계산
    print(f"Execution time: {elapsed_time} seconds")
    return {"result": "ok"}

@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    start_time = time.time()
    file_name = file.filename.split(".")[0]
    result = whisper_x.process_video(file, output_dir = "./stt_output/{output_dir}.json".format(output_dir=file_name))
    json2qdrant.initialize_qdrant_collection(encoder, client, result, "STT")
    end_time = time.time()  # 실행 종료 시간 기록
    elapsed_time = end_time - start_time  # 경과 시간 계산
    print(f"Execution time: {elapsed_time} seconds")
    return {"result": "ok"}

@app.post("/search")
async def search_qdrant(search_request: SearchRequest):
    collection_name = search_request.collection_name
    search_text = search_request.search_text
    dataframe = search.query2docs(collection_name, search_text, 10, client, encoder)
    return {"result": dataframe.to_dict()}

@app.post("/delete-collection/{delete_collection_name}")
async def delete_collection(delete_collection_name: str):
    try:
        client.delete_collection(delete_collection_name,timeout=1)
    except Exception as e:
        print(f"Qdrant docker delete Exception - {e}")
    try :
        client.create_collection(delete_collection_name,vectors_config=VectorParams(size=768, distance=Distance.COSINE))
    except Exception as e:
        print(f"Qdrant docker create Exception - {e}")

    return {"result": "hello"}

@app.post("/hello")
async def hello():
    return JSONResponse(content={"result": "hello"})

@app.post("/pdf-parse")
async def process_pdf(request: PdfParseRequest): # 경로는 main.py 기준
    option = request.option
    dir_path = request.dir_path
    script_json_name = request.script_json_name
    if option == '원고 or 단신':
        print('원고 or 단신')
        output_json = script2json.process_main(directory_path=dir_path)
        json2qdrant.initialize_qdrant_collection(encoder, client, output_json, "pdf_script")
    elif option == '자막':
        print('자막')
        output_json = subtitle2json.process_main(directory_path=dir_path, script_json_name=script_json_name)
        json2qdrant.initialize_qdrant_collection(encoder, client, output_json, "pdf_subtitle")
    print("작업 완료")

    return JSONResponse(content={"result": output_json})
