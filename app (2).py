import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import io

st.title("Fast & High-Quality Image Converter")

def image_bytes_to_pil(file_bytes):
    return Image.open(io.BytesIO(file_bytes))

@st.cache_data(show_spinner=False)
def process_image(image_bytes, op, params):
    img = image_bytes_to_pil(image_bytes)
    if op == "Grayscale":
        img = img.convert("L")
    elif op == "Rotate":
        img = img.rotate(params["degree"], expand=True, resample=Image.BICUBIC)
    elif op == "Resize":
        img = img.resize((int(params["width"]), int(params["height"])), Image.LANCZOS)
    elif op == "Enhance Sharpness":
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(params["factor"])
    elif op == "Blur":
        img = img.filter(ImageFilter.GaussianBlur(params["amount"]))
    # No change for "None" or "Convert to PNG"
    return img

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    image = image_bytes_to_pil(file_bytes)
    st.image(image, caption="Original Image", use_container_width=True)

    st.subheader("Choose an operation to perform:")
    op = st.selectbox(
        "Select Image Conversion",
        ("Grayscale", "Rotate", "Resize", "Enhance Sharpness", "Blur", "Convert to PNG", "None")
    )

    params = {}
    if op == "Rotate":
        params["degree"] = st.slider("Rotate by degrees:", 0, 360, 90)
    elif op == "Resize":
        params["width"] = st.number_input("Width:", min_value=1, value=image.width)
        params["height"] = st.number_input("Height:", min_value=1, value=image.height)
    elif op == "Enhance Sharpness":
        params["factor"] = st.slider("Enhancement factor:", 1.0, 5.0, 2.0)
    elif op == "Blur":
        params["amount"] = st.slider("Blur radius:", 1, 10, 2)

    if op != "Convert to PNG" and op != "None":
        processed_img = process_image(file_bytes, op, params)
    else:
        processed_img = image

    st.subheader("Processed Image")
    st.image(processed_img, use_container_width=True)

    buf = io.BytesIO()
    output_format = "PNG" if op=="Convert to PNG" or uploaded_file.type=="image/png" else "JPEG"
    processed_img.save(buf, format=output_format, quality=95)
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Image",
        data=byte_im,
        file_name=f"converted_image.{output_format.lower()}",
        mime=f"image/{output_format.lower()}"
    )
