import pytesseract
from pytesseract import Output
import os
import argparse
import helper


# process one image, create metadata and return
def ocr_one_image(the_image):
    meta_data_dict = {"not_email_or_website": None, "email": None, "website": None}
    not_email_or_website = []
    email = []
    website = []

    # ocr the image and set necessary parameters
    output = pytesseract.image_to_data(the_image, output_type=Output.DICT)
    the_text = output["text"]
    the_length = len(the_text)
    the_count = 0

    while the_count < the_length:
        all_str = ""
        if the_text[the_count] != "" or the_text[the_count] != " ":
            for text_i in range(the_count, the_length):
                cur_text = the_text[text_i]
                if cur_text != "":
                    if helper.is_email(cur_text):
                        email.append(cur_text)
                    elif helper.is_website(cur_text):
                        website.append(cur_text)
                    else:
                        all_str += cur_text + " "
                    the_count = text_i
                else:
                    the_non_empty_index = text_i
                    for text_x in range(the_non_empty_index, the_length):
                        if the_text[text_x] != '' and the_text[text_x] != " ":
                            the_count = text_x - 1
                            break
                    break
            if all_str != "" and all_str != "  ":
                all_str = all_str[:len(all_str)-1]  # remove the last empty character (" ")
                not_email_or_website.append(all_str)
        the_count += 1

    meta_data_dict["not_email_or_website"] = not_email_or_website
    meta_data_dict["email"] = email
    meta_data_dict["website"] = website

    return meta_data_dict


if __name__ == '__main__':
    # set up arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--folder", required=True,
                    help="path to the folder containing images to be used")
    ap.add_argument("-m", "--mode", type=int, default=0,
                    help="enter what you want to extract. Modes:\n "
                         "0 - all\n"
                         "1 - email"
                         "2 - website")
    args = vars(ap.parse_args())
    folder = args["folder"]
    mode = args["mode"]

    valid_modes = [0, 1, 2]
    functions = [helper.always_true, helper.is_email, helper.is_website]

    if mode not in valid_modes:
        print("please enter a valid mode")
        exit()

    for i in range(len(os.listdir(folder))):
        # open the appropriate file
        if mode == 0:
            f = open(r"D:\Dersler\CS\Staj\JotForm\all.txt", "a", encoding='utf-8')
        elif mode == 1:
            f = open(r"D:\Dersler\CS\Staj\JotForm\emails.txt", "a", encoding='utf-8')
        elif mode == 2:
            f = open(r"D:\Dersler\CS\Staj\JotForm\urls.txt", "a", encoding='utf-8')

        image = helper.load_image_from_folder(folder, i)

        out = pytesseract.image_to_data(image, output_type=Output.DICT)
        text = out["text"]
        length = len(text)
        count = 0
        starts_with_space = True  # to prevent printing empty spaces on the console if the text contains empty elements.

        while count < length:
            if text[count] != "" or text[count] != " ":
                for k in range(count, length):
                    if text[k] != "":
                        if functions[mode](text[k]):
                            print(text[k], " ", end="")
                            # write the text evaluated from the image into a file.
                            f.write(text[k].ljust(50) + "image-" + str(i) + "\n")
                            starts_with_space = False
                            count = k
                    else:
                        non_empty_index = k
                        for x in range(non_empty_index, length):
                            if text[x] != '' and text[x] != " ":
                                count = x - 1
                                if not starts_with_space:
                                    print()
                                break
                        break
            count += 1

        print("\n")