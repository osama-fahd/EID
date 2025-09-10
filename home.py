import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import arabic_reshaper
from bidi.algorithm import get_display
import os
import zipfile

st.set_page_config(
    page_title="moneymoon Invitation Cards",
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
            float: left;
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
        "title": "moneymoon Invitation Card Generator",
        "sidebar_text": "Developed by moneymoon's team",
        "greeting": "Please type the invitees' names (one name per line) and click the button to get the invitation cards.",
        "name_label": "Names:",
        "generate_button": "Generate Invitation Cards",
        "caption": "Invitation card for",
        "download_one": "Download this Card",
        "download_all": "Download All Cards (.zip)",
        "warning": "Please enter at least one name.",
        "download_all_note": "Note: After generating, a button to download all cards at once will appear at the very bottom of the page.",
        "generation_success": "✅ All cards generated! You can download them all at once using the final button below."
    },
    "Arabic": {
        "title": " بطاقات دعوة موني مون",
        "sidebar_text": "تم التطوير بواسطة فريق موني مون",
        "greeting": """يرجى كتابة أسماء المدعوين (اسم واحد في كل سطر) والضغط على الزر للحصول على بطاقات الدعوة""",
        "name_label": "الأسماء:",
        "generate_button": "إنشاء بطاقات الدعوة",
        "caption": "بطاقة دعوة لـ",
        "download_one": "تحميل هذه البطاقة",
        "download_all": "تحميل جميع البطاقات (ملف مضغوط)",
        "warning": "يرجى إدخال اسم واحد على الأقل.",
        "download_all_note": "ملاحظة: بعد الإنشاء، سيظهر زر في أسفل الصفحة لتحميل جميع البطاقات مرة واحدة.",
        "generation_success": "✅ تم إنشاء جميع البطاقات! يمكنك تحميلها جميعًا مرة واحدة باستخدام الزر النهائي أدناه."
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

st.info(texts['download_all_note'])

if st.button(texts["generate_button"]):
    names_list = [name.strip() for name in names_input.splitlines() if name.strip()]

    if not names_list:
        st.warning(texts['warning'])
    else:
        generated_images_for_zip = []

        for name in names_list:
            with st.container():
                st.markdown("---")
                img = create_image_with_name(name)

                st.image(img, caption=f"{texts['caption']} {name}")

                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes_value = img_bytes.getvalue()

                st.download_button(
                    label=f"📥 {texts['download_one']}",
                    data=img_bytes_value,
                    file_name=f"Invitation_Card_{name}.png",
                    mime="image/png",
                    key=f"download_single_{name}"
                )

                file_name_for_zip = f"Invitation_Card_{name}.png"
                generated_images_for_zip.append((file_name_for_zip, img_bytes_value))

        if generated_images_for_zip:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_name, data in generated_images_for_zip:
                    zf.writestr(file_name, data)

            zip_buffer.seek(0)

            st.markdown("---")
            st.success(texts['generation_success'])

            st.download_button(
                label=f"📂 {texts['download_all']}",
                data=zip_buffer,
                file_name="All_Invitation_Cards.zip",
                mime="application/zip",
                key="download_all_zip"
            )