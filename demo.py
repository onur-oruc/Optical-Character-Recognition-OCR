import streamlit as st
import tesseract_model
from PIL import Image
import numpy as np
import os
import json


def process_ocr(folder_path_="."):
    json_object = []

    for i in range(len(os.listdir(folder_path_))):
        # 1. join file an folder path
        # 2. read the image with a similar function below
        img = Image.open(os.path.join(folder_path_, "img-" + str(i) + ".jpg"))
        img = np.array(img)
        st.image(img)
        st.write("image" + str(i))
        # 3. apply ocr to image by calling ocr_one_image(image)
        image_meta_data_ = tesseract_model.ocr_one_image(img)
        json_object.append(image_meta_data_)
        st.write(image_meta_data_)
        if i == 555:
            break
    # write all the information extracted from images into a json file.
    file = os.path.join(os.getcwd(), "meta_data.json")
    print(os.getcwd())
    with open(file, "w") as jsonfile:
        json.dump(json_object, jsonfile)
        st.write("json created 1")
    # stlit.write("json created 2")
    # f = open(file, "r")
    # data = json.load(f)
    # stlit.write(data)


st.title("OCR tool to detect texts on logos and images in user emails")
st.markdown("Welcome to the demo.")
# -- Heroku Deployment --
# Now that we have our application it would be nice if we could host it online somewhere.

options = np.array(["Upload From A Directory", "Upload Manually"])
option = st.selectbox("Choose your method: ", options)

if option.title() == options[0]:  # upload from the directory
    directory_options = ["Select Images From Current Directory", "Change Directory"]
    directory_option = st.selectbox("Directory Location", directory_options)

    if directory_option.title() == directory_options[0]:  # current directory
        folder_path = '.'
        st.write('You selected `%s`' % folder_path)
        # todo first list the files in the current directory HERE
        if st.button("start"):
            process_ocr(folder_path)
    elif directory_option.title() == directory_options[1]:  # another directory
        folder_path = st.text_input('Enter folder path', '.')
        if st.button("start"):
            process_ocr(folder_path)
            # f2 = open("meta_data_json.json",)
            # data = json.load(f2)
            # for info in data:
            #     if info["email"]:
            #         stlit.write(info["email"])
            st.write('You selected `%s`' % folder_path)
elif option.title() == options[1]:  # upload manually
    uploaded_images = st.file_uploader("Choose an image", accept_multiple_files=True)

    for uploaded_image in uploaded_images:
        image = Image.open(uploaded_image)
        image_array = np.array(image)  # convert the image to numpy array for the tesseract model to perform better
        st.image(image_array)
        image_meta_data = tesseract_model.ocr_one_image(image_array)
        st.write(image_meta_data)

