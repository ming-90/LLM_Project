import streamlit as st
import requests
import pandas as pd
import os
import time
import json

def seconds_to_min_sec(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes}:{seconds:02d}"

def read_first_json_from_directory(directory):
    """
    지정된 디렉토리에서 첫 번째 JSON 파일의 내용을 읽어서 반환합니다.
    """
    # 디렉토리 내의 모든 파일 목록을 가져옵니다.
    files = os.listdir(directory)

    # 파일 목록을 순회하며 JSON 파일을 찾습니다.
    for file_name in files:
        if file_name.endswith('.json'):
            # JSON 파일 경로를 구성합니다.
            file_path = os.path.join(directory, file_name)

            # JSON 파일을 열고 내용을 읽습니다.
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data  # JSON 데이터 반환

    # JSON 파일이 디렉토리에 없는 경우
    return None

class videoSTT:
    class Model:
        pageTitle = "Video Speech To Text"

    def view(self, model):
        if "prev_dict" not in st.session_state:
            st.session_state["prev_dict"] = {}

        if "uploaded_file_STT" not in st.session_state:
            st.session_state["uploaded_file_STT"] = None

        if "processing" not in st.session_state:
            st.session_state["processing"] = False

        if "processed" not in st.session_state:
            st.session_state["processed"] = False

        if "response" not in st.session_state:
            st.session_state["response"] = False

        st.title(f"🗣 {model.pageTitle}")
        upload_file = st.file_uploader("Choose a video file", type=["mp4"])

        ### main view ###
        # 프로세스 실행 전
        if st.session_state["processing"] == False and st.session_state["processed"] == False:
            print("프로세스 실행 전")

        # 프로세스 실행 중
        if st.session_state["processing"] == True and st.session_state["processed"] == False:
            st.write("파일 처리 중입니다.")
            with st.empty():
                while True:
                    if os.listdir("./server/stt_output"):
                        print("결과 존재")
                        st.session_state["processed"] = True
                        st.session_state["processing"] = False
                        st.session_state["response"] = read_first_json_from_directory("./server/stt_output")
                        print("파일떨궈졌으니 세션 변경")
                        st.rerun()
                    time.sleep(5)  # 5초마다 확인
                    print("서버 상태 확인")


        # 프로세스 완료
        if st.session_state["processing"] == False and st.session_state["processed"] == True:
            col1, col2 = st.columns([0.5, 0.5], gap="small")

            with col2:
                content_data = st.session_state["response"]["script"]["content"]
                df = pd.DataFrame(content_data)[["start", "text"]] # df 생성
                df['start_time'] = df['start'].apply(seconds_to_min_sec) # 분 초 보기좋게
                rows_count = df.shape[0] # df크기 조절용 개수세기
                df_display = df[['start_time', 'text']]
                df_display['link'] = False
                # 데이터 에디터에 df 표시
                st.data_editor(df_display, key="time_line", use_container_width=True, hide_index=True, height=rows_count*37+4)

                new_dict = st.session_state["time_line"]["edited_rows"]

                # 활성화된 인덱스 (Is Endangered가 true로 설정된 경우)
                activated_indexes_stt = [int(key) for key, value in new_dict.items() if value.get("link", False) is True]

                # 비활성화된 인덱스 (Is Endangered가 false로 설정된 경우)
                deactivated_indexes_stt = [int(key) for key, value in new_dict.items() if value.get("link", True) is False]

                # 활성화된 인덱스에 대한 처리
                if activated_indexes_stt:
                    # 활성화된 인덱스에 대한 start_time을 세션 상태에 저장
                    activated_start_times = [df['start'][idx] for idx in activated_indexes_stt]
                    st.session_state["activated_indexes_stt"] = activated_start_times

                # 비활성화된 인덱스에 대한 처리
                if deactivated_indexes_stt:
                    # 비활성화된 인덱스에 대한 start_time을 세션 상태에 저장 (필요한 경우)
                    deactivated_start_times = [df['start'][idx] for idx in deactivated_indexes_stt]
                    if "deactivated_indexes_stt" not in st.session_state:
                        st.session_state["deactivated_indexes_stt"] = deactivated_start_times
                    else:
                        # 비활성화된 인덱스 처리 로직 (예: deactivated_indexes_stt 목록에서 제거)
                        st.session_state["deactivated_indexes_stt"] = [time for time in st.session_state["deactivated_indexes_stt"] if time not in deactivated_start_times]

            with col1:
                if st.session_state.get("activated_indexes_stt"):
                    # 새 인덱스 기반으로 시작 시간 설정하여 비디오 재생
                    st.video(st.session_state["uploaded_file_STT"], start_time=int(st.session_state["activated_indexes_stt"][-1]))
                else:
                    st.video(st.session_state["uploaded_file_STT"])
        if upload_file is not None:
            # if st.button("Process"):
            #     st.session_state["uploaded_file_STT"] = upload_file
            #     st.session_state["processing"] = True
            #     files = {"file": (st.session_state["uploaded_file_STT"].name, st.session_state["uploaded_file_STT"], "video/mp4")}
            #     response = requests.post("http://localhost:8000/process-video", files=files)
            #     if response.status_code == 200:
            #         st.session_state["processing"] = False
            #         st.session_state["processed"] = True
            #         st.session_state["response"] = read_first_json_from_directory("./server/stt_output")
            #         print("서버에서 완료됨")
            #         st.rerun()
            #     else:
            #         st.error("파일 처리 실패")
            if st.button("STT test"):
                st.session_state["uploaded_file_STT"] = upload_file
                st.session_state["processing"] = False
                st.session_state["processed"] = True
                st.session_state["response"] = read_first_json_from_directory(f"./server/stt_output")


        # if st.button("delete", type="primary"):
        #     st.session_state["uploaded_file_STT"] = None
        #     st.session_state["processing"] = False
        #     st.session_state["processed"] = False
        #     st.session_state["response"] = False

        #     for filename in os.listdir("./server/stt_output"):
        #         file_path = os.path.join("./server/stt_output", filename)
        #         try:
        #             if os.path.isfile(file_path) or os.path.islink(file_path):
        #                 os.unlink(file_path)
        #         except Exception as e:
        #             print(f'Failed to delete {file_path}. Reason: {e}')
        #     st.rerun()