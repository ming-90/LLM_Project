import streamlit as st
from views.searchNews import searchNews
from views.pdfParser import pdfParser
from views.videoSTT import videoSTT
from views.chat_Triz import chatVideo

from streamlit_option_menu import option_menu

# ------------------------------------------------------------------------------
# Main Page Setup

st.set_page_config(
    page_title="Triz",
    page_icon="favicon.png",
    layout="wide"
)

# Remove made by Streamlit footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------------------------------------------------------------------

class Model:
    menuTitle = "Triz helper"

    chatVideo = "Triz"

    menuIcon = "pencil-fill"
    sttIcon = "soundwave"


def view(model):
    with st.sidebar:
        menuItem = option_menu(model.menuTitle,
                               [model.chatVideo],
                               icons=[model.sttIcon],
                               menu_icon=model.menuIcon,
                               default_index=0,
                               styles={
                                   "container": {"padding": "5!important", "background-color": "#fafafa"},
                                   "icon": {"color": "black", "font-size": "15px"},
                                   "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px","--hover-color": "#eee"},
                                   "nav-link-selected": {"background-color": "#037ffc"},
                               }
                    )

    # if menuItem == model.searchNews:
    #     searchNews().view(searchNews.Model())
    # elif menuItem == model.videoSTT:
    #     videoSTT().view(videoSTT.Model())
    if menuItem == model.chatVideo:
        chatVideo().view(chatVideo.Model())

view(Model())
