import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import arabic_reshaper
from bidi.algorithm import get_display
import os

st.set_page_config(
    page_title="Moneymoon Eid Images",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌙",
)

# Inject Custom CSS for RTL Support
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

# Initialize session state for language
if "language" not in st.session_state:
    st.session_state.language = "English"

# Language toggle function
def toggle_language():
    if st.session_state.language == "English":
        st.session_state.language = "Arabic"
    else:
        st.session_state.language = "English"

# Inject RTL CSS
inject_custom_css()

# Define translations
translations = {
    "English": {
        "title": "Moneymoon Eid Images! 🎉",
        "sidebar_text": "Developed by Moneymoon's team",
        "greeting": "Moneymoon family wishes you a happy Eid Al-Adha! Please type your name and click the button to get your Eid Al-Adha 2025 greeting card!",
        "name_label": "Name:",
        "generate_button": "Generate Eid Image",
        "caption": "Your Eid Image",
        "download": "Download the Image!",
    },
    "Arabic": {
        "title": "عيد موني مون!🎉 ",
        "sidebar_text": "تم التطوير بواسطة فريق موني مون",
        "greeting": """عائلة موني مون تتمنى لكم عيد أضحى سعيد!
يرجى كتابة اسمك والضغط على الزر للحصول على بطاقة تهنئة عيد الأضحى""",
        "name_label": "الاسم:",
        "generate_button": "إنشاء بطاقة التهنئة",
        "caption": "صورتك للعيد",
        "download": "تحميل الصورة!",
    }
}

# Get the current language texts
lang = st.session_state.language
texts = translations[lang]

# Sidebar
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


def create_image_with_name(name, template_path="./Moneymoon-Eid.jpg"):
    # Open the template image
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    # Reshape and fix Arabic text direction
    reshaped_text = arabic_reshaper.reshape(name)
    bidi_text = get_display(reshaped_text)

    # Load custom Arabic font
    font_path = os.path.join("fonts", "Amiri-Regular.ttf")  # Ensure this file exists!
    try:
        font = ImageFont.truetype(font_path, size=80)
    except IOError:
        font = ImageFont.load_default()  # Fallback, but won't support Arabic

   # Get text size
    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Get image size
    img_width, img_height = img.size

    # Center horizontally
    x = (img_width - text_width) / 2

    # Move text up from the bottom (e.g. 150 pixels)
    y = img_height - text_height - 400

    # Draw text
    draw.text((x, y), bidi_text, font=font, fill="#white")




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
        file_name="eid_image.png",
        mime="image/png",
    )
