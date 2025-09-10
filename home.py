import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import arabic_reshaper
from bidi.algorithm import get_display
import os
import zipfile # IMPORTED: Required for creating ZIP files

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
        .stTextArea > div > div > textarea, .stTextInput > div > div > input {
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
        "title": "Moneymoon Invitation Card Generator",
        "sidebar_text": "Developed by Moneymoon's team",
        "greeting": "Please type the invitees' names (one name per line) and click the button to get the invitation cards.",
        "name_label": "Names:",
        "generate_button": "Generate Invitation Cards",
        "caption": "Invitation card for",
        # MODIFIED: Changed "Download Image" to a new key for the ZIP button
        "download_all": "Download All Cards (.zip)",
        "warning": "Please enter at least one name."
    },
    "Arabic": {
        "title": " بطاقات دعوة موني مون",
        "sidebar_text": "تم التطوير بواسطة فريق موني مون",
        "greeting": """يرجى كتابة أسماء المدعوين (اسم واحد في كل سطر) والضغط على الزر للحصول على بطاقات الدعوة""",
        "name_label": "الأسماء:",
        "generate_button": "إنشاء بطاقات الدعوة",
        "caption": "بطاقة دعوة لـ",
        # MODIFIED: Changed "Download Image" to a new key for the ZIP button (Arabic)
        "download_all": "تحميل جميع البطاقات (ملف مضغوط)",
        "warning": "يرجى إدخال اسم واحد على الأقل."
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
        font = ImageFont.truetype(font_path, size=70)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), bidi_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img_width, img_height = img.size
    x = (img_width - text_width) / 2
    y = (img_height - text_height) / 2 - 50

    draw.text((x, y), bidi_text, font=font, fill="#43FFAE")

    return img


st.write(texts["greeting"])
names_input = st.text_area(texts["name_label"], height=200)

# MODIFIED: Reworked the entire logic to generate a single ZIP file
if st.button(texts["generate_button"]):
    names_list = [name.strip() for name in names_input.splitlines() if name.strip()]

    if not names_list:
        st.warning(texts['warning'])
    else:
        # Create a list to hold the generated image data in memory
        generated_images = []
        
        # --- Step 1: Generate all images and display them ---
        st.markdown("---")
        for name in names_list:
            img = create_image_with_name(name)
            
            # Display the generated card to the user
            st.image(img, caption=f"{texts['caption']} {name}")
            
            # Convert image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            
            # Prepare filename and store it with the image bytes
            file_name = f"Invitation_Card_{name}.png"
            generated_images.append((file_name, img_bytes.getvalue()))
        
        # --- Step 2: Create a ZIP file in memory ---
        zip_buffer = io.BytesIO()
        # The 'with' statement ensures the zip file is properly closed
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Write each generated image into the zip file
            for file_name, data in generated_images:
                zf.writestr(file_name, data)
        
        zip_buffer.seek(0) # Rewind the buffer to the beginning

        # --- Step 3: Provide a single download button for the ZIP file ---
        st.markdown("---")
        st.download_button(
            label=f"📂 {texts['download_all']}",
            data=zip_buffer,
            file_name="All_Invitation_Cards.zip",
            mime="application/zip",
        )