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
    page_icon="🎉",
)

def inject_custom_css():
    rtl_css = """
    <style>
        body {
            direction: rtl;
            text-align: right;
        }
        .stButton > button {
            float: left;
        }
        .stTextArea > div > div > textarea, .stTextInput > div > div > input {
            text-align: right;
        }
        .stTitle, .stHeader, .stMarkdown {
            text-align: right;
        }
        /* This hides the "Press Enter to apply" text entirely */
        div[data-testid="InputInstructions"] {
            display: none !important;
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

# English and Arabic translations as specified
translations = {
    "English": {
        "title": "Moneymoon Eid Images! 🎉",
        "sidebar_text": "Developed by Moneymoon's team",
        "greeting": "Moneymoon family wishes you a happy Eid Al-Fitr! Please type your name and click the button to get your Eid Al-Fitr 2026 greeting card!",
        "name_label": "Name:",
        "generate_button": "Generate Eid Image",
        "caption": "Your Eid Image",
        "download": "Download the Image!",
        "warning": "Please enter your name."
    },
    "Arabic": {
        "title": "عيد موني مون! 🎉",
        "sidebar_text": "تم التطوير بواسطة فريق موني مون",
        "greeting": "عائلة موني مون تتمنى لكم عيد فطر سعيد! يرجى كتابة اسمك والضغط على الزر للحصول على بطاقة تهنئة عيد الفطر!",
        "name_label": "الاسم:",
        "generate_button": "إنشاء بطاقة التهنئة",
        "caption": "صورتك للعيد",
        "download": "تحميل الصورة!",
        "warning": "يرجى إدخال الاسم."
    }
}

lang = st.session_state.language
texts = translations[lang]

with st.sidebar:
    # Ensure the MM-LOGO.png file is in the correct path
    try:
        st.image("./MM-LOGO.png")
    except:
        pass # Silently pass if logo is missing during testing
        
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

# Updated function to position text at the bottom
def create_image_with_name(name, template_path="./Eid_Template.jpg"):
    # Ensure Eid_Template.jpg is present in the correct path
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    reshaped_text = arabic_reshaper.reshape(name)
    bidi_text = get_display(reshaped_text)

    font_path = os.path.join("fonts", "DINNextLTArabic-Regular_0.ttf")
    try:
        font = ImageFont.truetype(font_path, size=70)
    except IOError:
        st.error(f"Font file not found at {font_path}! Using default font.")
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img_width, img_height = img.size
    
    # x is still centered
    x = (img_width - text_width) / 2
    
    # !!! NEW Y CALCULATION !!!
    # y = image height - text height - margin from bottom
    y = img_height - text_height - 180 

    draw.text((x, y), bidi_text, font=font, fill="#43FFAE")

    return img

st.write(texts["greeting"])

# Input for a single name
name_input = st.text_input(texts["name_label"])

if st.button(texts["generate_button"]):
    name = name_input.strip()

    if not name:
        st.warning(texts['warning'])
    else:
        with st.container():
            st.markdown("---")
            # Ensure 'Eid_Template.jpg' exists in the directory.
            try:
                img = create_image_with_name(name, template_path="./Eid-Greeting2.jpg")
                
                st.image(img, caption=f"{texts['caption']} - {name}")

                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes_value = img_bytes.getvalue()

                st.download_button(
                    label=f"📥 {texts['download']}",
                    data=img_bytes_value,
                    file_name=f"Eid_Card_{name}.png",
                    mime="image/png",
                )
            except FileNotFoundError:
                st.error("Template image not found! Please make sure 'Eid_Template.jpg' exists in the directory.")