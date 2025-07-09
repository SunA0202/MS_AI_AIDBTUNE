import streamlit as st
from streamlit_option_menu import option_menu
import menu1, menu2, menu3

st.set_page_config(page_title="SA AIDB TUNE", layout="wide")
# st.title('Streamlit 앱의 테마 사용자 정의하기')


# sidebar 설정
menu1_title = "📊ERD 조회"
menu2_title = "🗂️Table Tuning"
menu3_title = "📝SQL Tuning"

with st.sidebar:
    choice = option_menu(
        "SA AIDB TUNE",
        [menu1_title, menu2_title, menu3_title],
        icons=['house', 'kanban', 'bi bi-robot'],
        menu_icon="app-indicator",
        default_index=0,
        styles={
            "container": {"padding": "4!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
            "nav-link-selected": {"background-color": "#08c7b4"},
        }
    )

if choice == menu1_title:
    st.header(menu1_title)
    st.markdown("<hr>", unsafe_allow_html=True)
    menu1.menu1_ui()
elif choice == menu2_title:
    st.header(menu2_title)
    menu2.menu2_ui()
elif choice == menu3_title:
    st.header(menu3_title)
    menu3.menu3_ui()