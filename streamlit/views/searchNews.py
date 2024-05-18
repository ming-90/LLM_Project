import streamlit as st
import requests
import pandas as pd

def seconds_to_min_sec(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes}:{seconds:02d}"

class searchNews:
    class Model:
        pageTitle = "Search in Video text"

    def view(self, model):

        if "uploaded_file_OCR" not in st.session_state:
            st.session_state["uploaded_file_OCR"] = None

        st.title(f"📄👀 {model.pageTitle}")
        upload_file = st.file_uploader("Choose a video file", type=["mp4"])
        if upload_file is not None:
            if st.button("OCR test"):
                st.session_state["uploaded_file_OCR"] = upload_file


        if st.session_state["uploaded_file_OCR"] is not None:
            col1, col2 = st.columns([0.6, 0.4], gap="small")

            with col2:
                words = st.text_input("Search Words", key="words")

                if words:
                    search_collection_name = "OCR"
                    response = requests.post(f"http://localhost:8000/search", json={"collection_name": search_collection_name, "search_text": words})
                    # 검색 기능을 파일 기반으로 사용하려면 query2docs 함수의 로직을 파일 내용 처리가 가능하도록 수정해야 합니다.
                    # 아래는 예시 코드이며, 실제 구현은 파일 내용에 따라 달라질 수 있습니다.
                    data = response.json()["result"]
                    df = pd.DataFrame(data)[["score","time", "text"]] # df 생성
                    df['start_time'] = df['time'].apply(seconds_to_min_sec) # 분 초 보기좋게
                    rows_count = df.shape[0] # df크기 조절용 개수세기
                    df_display = df[['start_time', 'text']].copy()
                    df_display.loc[:, 'link'] = False
                    # 데이터 에디터에 df 표시
                    st.data_editor(df_display, key="time_line", use_container_width=True, hide_index=True, height=rows_count*37+4)

                    new_dict = st.session_state["time_line"]["edited_rows"]

                    # 활성화된 인덱스 (Is Endangered가 true로 설정된 경우)
                    activated_indexes_ocr = [int(key) for key, value in new_dict.items() if value.get("link", False) is True]

                    # 비활성화된 인덱스 (Is Endangered가 false로 설정된 경우)
                    deactivated_indexes_ocr = [int(key) for key, value in new_dict.items() if value.get("link", True) is False]

                    # 활성화된 인덱스에 대한 처리
                    if activated_indexes_ocr:
                        # 활성화된 인덱스에 대한 start_time을 세션 상태에 저장
                        activated_start_times = [df['time'][idx] for idx in activated_indexes_ocr]
                        st.session_state["activated_indexes_ocr"] = activated_start_times

                    # 비활성화된 인덱스에 대한 처리
                    if deactivated_indexes_ocr:
                        # 비활성화된 인덱스에 대한 start_time을 세션 상태에 저장 (필요한 경우)
                        deactivated_start_times = [df['time'][idx] for idx in deactivated_indexes_ocr]
                        if "deactivated_indexes_ocr" not in st.session_state:
                            st.session_state["deactivated_indexes_ocr"] = deactivated_start_times
                        else:
                            # 비활성화된 인덱스 처리 로직 (예: deactivated_indexes_ocr 목록에서 제거)
                            st.session_state["deactivated_indexes_ocr"] = [time for time in st.session_state["deactivated_indexes_ocr"] if time not in deactivated_start_times]
            with col1:
                if st.session_state.get("activated_indexes_ocr"):
                    # 새 인덱스 기반으로 시작 시간 설정하여 비디오 재생
                    st.video(st.session_state["uploaded_file_OCR"], start_time=int(st.session_state["activated_indexes_ocr"][-1]))
                else:
                    st.video(st.session_state["uploaded_file_OCR"])