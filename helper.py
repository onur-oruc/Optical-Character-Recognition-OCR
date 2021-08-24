import cv2
import os
import numpy as np
import skimage.color
import skimage.filters
import skimage.io
import re


def rename_all_images_in_folder(folder, start_id):
    img_id = start_id
    for image in os.listdir(folder):
        old_file = os.path.join(folder, image)
        new_file = os.path.join(folder, "img-"+str(img_id)+".jpg")
        os.rename(old_file, new_file)
        img_id += 1


# return all images
def load_images_from_folder(folder):
    # print(folder)
    images = []
    for img_file in os.listdir(folder):
        # print(os.path.join(folder, img_file))
        img = cv2.imread(os.path.join(folder, img_file))
        if img is not None:
            images.append(img)

    return images


# return images one by one
def load_image_from_folder(folder, count):
    # print(folder)
    print(os.path.join(folder, "img-"+str(count)+".jpg"))
    return cv2.imread(os.path.join(folder, "img-"+str(count)+".jpg"))


def advanced_thresholding(img, sigma):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    # blur and grayscale before thresholding
    blur = skimage.color.rgb2gray(img)
    blur = skimage.filters.gaussian(blur, sigma=sigma)

    # perform inverse binary thresholding
    threshold = skimage.filters.threshold_otsu(blur)
    mask = blur < threshold

    # use mask to select the useful part of the image
    sel = np.zeros_like(img)
    sel[mask] = img[mask]
    cv2.imshow('image', sel)
    cv2.waitKey(0)

    return sel


def is_email(text):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, text):
        return True
    return False


def is_date(text):
    return False


def is_website(text):
    regex = r'\b(//|\s+|^)(\w\.|\w[A-Za-z0-9-]{0,61}\w\.){1,3}[A-Za-z]{2,6}\b'
    # regex2 = r'\b(//|\s+|^)(\w\.|\w[A-Za-z0-9-]{0,61}\w\[^ ]*.){1,3}[A-Za-z]{2,6}\b'
    if re.fullmatch(regex, text):
        return True
    return False


def always_true(text):
    return True


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY, cv2.THRESH_OTSU)[1]


# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)