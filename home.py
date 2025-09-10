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
        # MODIFIED: Updated greeting text for multiple names
        "greeting": "Please type the invitees' names (one name per line) and click the button to get the invitation cards.",
        # MODIFIED: Updated label for clarity
        "name_label": "Names:",
        "generate_button": "Generate Invitation Cards",
        "caption": "Invitation card for",
        "download": "Download Image",
        "warning": "Please enter at least one name."
    },
    "Arabic": {
        "title": "مولد بطاقات دعوة موني مون",
        "sidebar_text": "تم التطوير بواسطة فريق موني مون",
        # MODIFIED: Updated greeting text for multiple names (Arabic)
        "greeting": """يرجى كتابة أسماء المدعوين (اسم واحد في كل سطر) والضغط على الزر للحصول على بطاقات الدعوة""",
        # MODIFIED: Updated label for clarity (Arabic)
        "name_label": "الأسماء:",
        "generate_button": "إنشاء بطاقات الدعوة",
        "caption": "بطاقة دعوة لـ",
        "download": "تحميل الصورة",
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

# MODIFICATION 1: Changed st.text_input to st.text_area for multi-line input
names_input = st.text_area(texts["name_label"], height=200)

# MODIFICATION 2: Reworked the button logic to handle multiple names
if st.button(texts["generate_button"]):
    # Split the input string by new lines to get a list of names
    # Also, strip whitespace and ignore any empty lines
    names_list = [name.strip() for name in names_input.splitlines() if name.strip()]

    if not names_list:
        st.warning(texts['warning'])
    else:
        # Loop through each name provided
        for name in names_list:
            # Use a container to group the image and its download button
            with st.container():
                st.markdown("---") # Add a visual separator
                
                # Generate the image for the current name
                img = create_image_with_name(name)
                
                # Display the image with a personalized caption
                st.image(img, caption=f"{texts['caption']} {name}")

                # Convert image to bytes for the download button
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes = img_bytes.getvalue()

                # Create a download button for each specific image
                st.download_button(
                    label=f"{texts['download']} ({name})",
                    data=img_bytes,
                    # Create a unique filename for each card
                    file_name=f"Invitation_Card_{name}.png",
                    mime="image/png",
                    # IMPORTANT: Provide a unique key for each button inside a loop
                    key=f"download_{name}" 
                )