import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import arabic_reshaper
from bidi.algorithm import get_display
import os

st.set_page_config(
    page_title="Moneymoon Invitation Cards",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="✉️",
)


def inject_custom_css():
    rtl_css = """
    <style>
        body {
            direction: rtl;
            text-align: right;
        }
        .stButton > button {
            float: left;  /* Ensures button stays on the left side for Arabic */
        }
        .stTextInput > div > div > input {
            text-align: right;
        }
        .stTitle, .stHeader, .stMarkdown {
            text-align: right;
        }
    </style>
    """
    if st.session_state.language == "Arabic":
        st.markdown(rtl_css, unsafe_allow_html=True)


if "language" not in st.session_state:
    st.session_state.language = "English"

def toggle_language():
    if st.session_state.language == "English":
        st.session_state.language = "Arabic"
    else:
        st.session_state.language = "English"

inject_custom_css()

translations = {
    "English": {
        "title": "Moneymoon Invitation Card",
        "sidebar_text": "Developed by Moneymoon's team",
        "greeting": "Please type the invitee's name and click the button to get the invitation card.",
        "name_label": "Name:",
        "generate_button": "Generate Invitation Card",
        "caption": "Your Invitation Card",
        "download": "Download the Image!",
    },
    "Arabic": {
        "title": "بطاقة دعوة موني مون",
        "sidebar_text": "تم التطوير بواسطة فريق موني مون",
        "greeting": """يرجى كتابة اسم المدعو والضغط على الزر للحصول على بطاقة الدعوة""",
        "name_label": "الاسم:",
        "generate_button": "إنشاء بطاقة الدعوة",
        "caption": "صورتك للدعوة",
        "download": "تحميل الصورة!",
    }
}

lang = st.session_state.language
texts = translations[lang]

with st.sidebar:
    st.image("./MM-LOGO.png")
    st.button(
        "عربي" if st.session_state.language == "English" else "EN",
        key="lang_toggle",
        on_click=toggle_language
    )
    st.markdown(
        f"<div style='text-align: {'right' if st.session_state.language == 'Arabic' else 'left'};'>"
        f"{texts['sidebar_text']}</div>",
        unsafe_allow_html=True
    )

st.title(texts["title"])


def create_image_with_name(name, template_path="./Personal Invitation.jpg"):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    reshaped_text = arabic_reshaper.reshape(name)
    bidi_text = get_display(reshaped_text)

    font_path = os.path.join("fonts", "DINNextLTArabic-Regular_0.ttf")  
    try:
        font = ImageFont.truetype(font_path, size=80)
    except IOError:
        font = ImageFont.load_default() 

    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img_width, img_height = img.size
    x = (img_width - text_width) / 2
    y = (img_height - text_height) / 2 - 50  

    draw.text((x, y), bidi_text, font=font, fill="#43FFAE")
    # "#43FFAE"


    return img


st.write(texts["greeting"])
name = st.text_input(texts["name_label"])

img = None
if st.button(texts["generate_button"]):
    img = create_image_with_name(name)
    st.image(img, caption=texts["caption"])

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    st.download_button(
        label=texts["download"],
        data=img_bytes,
        file_name="Invitation_Card.png",
        mime="image/png",
    )
