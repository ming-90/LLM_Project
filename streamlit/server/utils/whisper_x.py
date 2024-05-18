import whisperx
from tempfile import NamedTemporaryFile
import json
import numpy as np
import os
from moviepy.editor import VideoFileClip
import re
import shutil
import time

def process_video(video_file, output_dir = "./stt_output/stt.json"): # 비디오 파일을 입력받아서 STT 결과를 JSON 파일로 저장\
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    with NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
        shutil.copyfileobj(video_file.file, tmpfile)
        tmpfile_path = tmpfile.name
    video = VideoFileClip(tmpfile_path)  # 임시 파일 경로 사용
    temp_audio_file = "temp_audio.wav"
    video.audio.write_audiofile(temp_audio_file)

    audio_numpy = whisperx.load_audio(temp_audio_file)

    device = "cpu" #cuda
    batch_size = 16
    compute_type = "int8" #float16

    model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    stt = model.transcribe(audio_numpy, batch_size=batch_size)

    model_a, metadata = whisperx.load_align_model(language_code=stt["language"], device=device)
    stt = whisperx.align(stt["segments"], model_a, metadata, audio_numpy, device, return_char_alignments=False)

    os.remove(temp_audio_file)

    result = transform_json_to_desired_format(stt)

    with open(output_dir, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    # with open(output_dir, 'r', encoding='utf-8') as f:
    #     result = json.load(f)

    return result

def transform_json_to_desired_format(input_json):
    content = [
        {
            "text": re.sub(r'\s+', ' ', segment["text"].strip()),
            "start": segment["start"],
            "end": segment["end"]
        }
        for segment in input_json["segments"]
    ]
    output_json = {"script": {"content": content}}

    return output_json