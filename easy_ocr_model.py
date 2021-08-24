import helper
import cv2
import argparse
import os
import torch
from easyocr import Reader
# import helper_functions.helper as helper


# clean up non-ASCII characters 'cause OpenCV's putText function
# cannot display them
def cleanup_text(text):
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--folder", required=True,
                help="path to the folder containing images to be used")
# ap.add_argument("-l", "--langs", type=str, default="en",
#                 help="comma separated list of languages to OCR")
ap.add_argument("-g", "--gpu", type=int, default=1,
                help="whether or not GPU should be used")
args = vars(ap.parse_args())

langs = ["ar", "en", "fa"]
print("[INFO] OCR'ing input folder...")


reader = Reader(langs, gpu=args["gpu"] > 0)
folder = args["folder"]
for i in range(len(os.listdir(folder))):
    image = helper.load_image_from_folder(folder, i)
    while True:
        try:
            results = reader.readtext(image)
            for (bbox, text, prob) in results:
                # display the OCR'd text and associated probability
                print("[INFO] {:.4f}: {}".format(prob, text))
                # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))

                text = cleanup_text(text)
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # show the output image
                # cv2.imshow("Image", image)
                cv2.waitKey(0)
        except RuntimeError:  # handle the situation "CUDA out of memory"
            del results
            del reader
            torch.cuda.empty_cache()
            reader = Reader(langs, gpu=args["gpu"] > 0)
            print("resetting the model...")
        break

