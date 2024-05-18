import streamlit as st
import os
import subprocess
import requests

def get_folder_path():
        path = os.path.abspath('src')
        p = subprocess.Popen(['python3','tkDirSelector.py'], cwd=path,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        result,error = p.communicate()
        p.terminate()
        if isinstance(result,bytes):
            return result.decode('utf-8')
        if isinstance(result,str):
            return result
        else:
            return "error occured"

class pdfParser:
    class Model:
        pageTitle = "Process MBC PDF data to Valuable Data"

    def view(self, model):
        st.title(f"💬 {model.pageTitle}")
        if 'dir_path' not in st.session_state:
            st.session_state['dir_path'] = "../input/test_script"
            st.session_state['script_json'] = None
            st.session_state['result'] = {}
        if st.session_state['script_json'] is not None:
            st.session_state['dir_path'] = "../input/test_subtitle"
        with st.container(border=True):
            if st.button('set folder path'):
                st.session_state['dir_path'] = get_folder_path()
            st.write(f'선택된 폴더 경로: {st.session_state["dir_path"]}')
            if st.session_state['dir_path'] is not None:
                if st.button('clear folder path',type="primary"):
                    st.session_state['dir_path'] = None
                if st.session_state['script_json'] is None:
                    option = st.selectbox(disabled=True,
                    label='변환하고자 하는 포맷을 선택하세요',
                    options=('원고 or 단신', ''))
                    option = "원고 or 단신"
                else:
                    option = st.selectbox(
                    '변환하고자 하는 포맷을 선택하세요',
                    ('자막', '원고 or 단신'))
                if st.button('process'):
                    with st.spinner('PDF를 처리하는 중입니다...'):
                        if option == "원고 or 단신":
                            st.session_state["script_json"] = "./output/" + (st.session_state['dir_path'].split("/")[-1])
                            response = requests.post(
                                "http://localhost:8000/pdf-parse",
                                json={"option": option, "dir_path": st.session_state['dir_path'],"script_json_name": st.session_state["script_json"]}
                            )
                        elif option == "자막":
                            response = requests.post(
                                "http://localhost:8000/pdf-parse",
                                json={"option": option, "dir_path": st.session_state['dir_path'], "script_json_name": st.session_state["script_json"]}
                            )
                        if response.status_code == 200:
                            st.session_state['result'] = response.json()
                            st.experimental_rerun() # 페이지 리로드
                        else:
                            st.error("파일 처리 실패.")
        if st.session_state['result'] != {}:
            st.success(f"pdf 처리 완료!")
            st.json(st.session_state['result'].get("result"))

