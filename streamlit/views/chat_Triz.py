import numpy as np
import streamlit as st
import pandas as pd
import requests

def reset_message():
    st.session_state.messages = []
    st.session_state.page = 0
    st.session_state.prompt = ""
    st.session_state.display = ""
    st.session_state.regenerate = False

def parse_principles(text):
    # 텍스트를 줄 단위로 분리
    lines = text.split('\n')
    # "원리"로 시작하는 줄만 선택
    principles = [line for line in lines if line.startswith('원리')]
    return principles

def choice_prin(principle):
    st.session_state.page += 1
    st.session_state.choice_principle = principle

class chatVideo:
    class Model:
        pageTitle = "chat TRIZ"
    def view(self, model):
        if "selected_content" not in st.session_state:
            st.session_state["selected_content"] = []
        if "page" not in st.session_state:
            st.session_state.page = 0
        if "choice_principle" not in st.session_state:
            st.session_state.choice_principle = ""
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o"
        if "display" not in st.session_state:
            st.session_state.display = ""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({"role": "system", "content": "Whatever questions you ask, divide them by table of contents and answer them with a line of inquiry and content must be written in Markdown format. Please start with \"#\" for the big topic"})

        st.title(f"{model.pageTitle}")

        col1, col2 = st.columns([0.7, 0.3], gap="small")
        with col1:
            st.caption("A Demo ")
        with col2:
            st.button("Reset", on_click=reset_message, args=None)

        if "principles" not in st.session_state:
            st.session_state.principles = []

        if "regenerate" not in st.session_state:
            st.session_state.regenerate = False

        if "prompt" not in st.session_state:
            st.session_state.prompt = ""

        index = 0

        if st.session_state.page == 0:
            prompt = st.chat_input("문제상황을 제시해주세요")
            if prompt:
                if st.session_state.prompt == "":
                    st.session_state.prompt = prompt  # Save the prompt to session state
                    print("prompt", st.session_state.prompt)
                response = requests.post("http://10.147.184.65:9700/inference/page0", data={"prompt": f"{st.session_state.prompt}",
                                                                                            "index": index})

                index += 1
                print("regenerate")
                print("regenerate", st.session_state.prompt)
                st.session_state.regenerate = False
                response = requests.post("http://10.147.184.65:9700/inference/page0", data={"prompt": f"{st.session_state.prompt}",
                                                                                        "index": index})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.display = data

            if st.session_state.regenerate:
                index += 1
                print("regenerate")
                print("regenerate", st.session_state.prompt)
                st.session_state.regenerate = False
                response = requests.post("http://10.147.184.65:9700/inference/page0", data={"prompt": f"{st.session_state.prompt}",
                                                                                        "index": index})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.display = data

            st.markdown(st.session_state.display)
            st.divider()
            if st.button("yes"):
                st.session_state.page += 1
                response = requests.post("http://10.147.184.65:9700/choice/page0", data={"choice_str": f"{st.session_state.display}"})
                st.session_state.regenerate = False
            if st.button("no"):
                st.session_state.regenerate = True

        elif st.session_state.page == 1:
            response = requests.post("http://10.147.184.65:9700/inference/page1", data={"prompt": f"{st.session_state.display}", # 트리즈 해줘 / 일반화 던져주기
                                                                                        "index": index})
            if response.status_code == 200:
                data = response.json()
                st.session_state.display = data # 저장
                st.session_state.principles = parse_principles(st.session_state.display) # 원리 추출
            st.caption("원리를 선택해주세요")
            if len(st.session_state.principles) > 0:
                for idx, principle in enumerate(st.session_state.principles):
                    st.button(f'{principle}', on_click=choice_prin, args=[principle])

            st.divider()
            st.markdown(st.session_state.display)

            if st.button("yes"):
                st.session_state.page += 1
                response = requests.post("http://10.147.184.65:9700/choice/page0", data={"choice_str": f"{st.session_state.display}"})
                st.session_state.regenerate = False
            if st.button("no"):
                st.session_state.principles = []
                st.session_state.regenerate = True


        elif st.session_state.page == 2:
            response = requests.post("http://10.147.184.65:9700/inference/page2", data={"prompt": f"{st.session_state.prompt}",
                                                                                        "index": index})
            if response.status_code == 200:
                data = response.json()
                st.session_state.display = data
            st.markdown(st.session_state.display)

        elif st.session_state.page == 3:
            response = requests.post("http://10.147.184.65:9700/inference/page3", data={"prompt": f"{st.session_state.prompt}",
                                                                                        "index": index})
            if response.status_code == 200:
                data = response.json()
                st.session_state.display = data
            st.markdown(st.session_state.display)

        if len(st.session_state.selected_content) > 0:
            for idx, res in enumerate(st.session_state.selected_content):
                st.button(f'{res}', on_click=sayhi, args=[res])
