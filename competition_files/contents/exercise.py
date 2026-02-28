import streamlit as st
import streamlit.components.v1 as components
from st_screen_stats import ScreenData

from utils import page_config, check_password

# --- Exercise Page Settings ---
EXERCISE_PAGE_URL = (
    "https://steelpipe75.github.io/inhouse-ml-competition-MDXQ-alumni-Mar/exercise/"
)

page_config()

st.title(":material/exercise: Exercise")

# 認証チェック
check_password()


def exercise() -> None:
    screenD = ScreenData(setTimeout=1000)
    data = screenD.st_screen_data()

    calculated_height = int(data["innerHeight"] * 0.9)
    iframe_height = max(calculated_height, 720)

    components.iframe(
        src=EXERCISE_PAGE_URL,
        width=data["innerWidth"],
        height=iframe_height,
    )
    st.link_button(
        ":material/tab: Exercise を別タブで開く",
        url=EXERCISE_PAGE_URL,
    )


exercise()
