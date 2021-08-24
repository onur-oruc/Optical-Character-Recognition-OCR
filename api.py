from jotform import *
import _thread as thread
import threading
import time
import os
import csv
import re
import urllib.request as urlreq
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.error import URLError
from collections import OrderedDict


authorized_key = 'XXX'
my_key = 'YYY'
fpath = 'ZZZ'
save_period = 1000
print("--start--")


# read form ids from the cvs file
def read_csv(file_path):
    form_ids = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        flag = False
        for row in csv_reader:
            if flag:
                form_ids.append(row[0])
            flag = True
    return form_ids


# fetch the images using their ids and return their URL's
def get_image_urls(form_ids, folder, interval, thread_num):
    jotform_api_client = JotformAPIClient(authorized_key)
    img_src_tag = 'img src="'
    img_urls = []
    count = 0

    for form_id in form_ids:
        if interval[0] < count <= interval[1]:
            if count % 100 == 0:
                print("thread number: ", thread_num, " count: ", count, " form_id: ", form_id)
            try:
                # if the form contains 'notification' or 'autorespond' type of emails
                form_properties = jotform_api_client.get_form_properties(form_id)
                if 'emails' in form_properties.keys():
                    for email in form_properties['emails']:
                        if isinstance(email, dict):  # to process the body part of the email, it should be a dictionary.
                            if 'body' in email.keys():
                                ebody = email['body']
                                indices = [i.start() for i in re.finditer(img_src_tag, ebody)]
                                for i in indices:
                                    url = escape_ascii(ebody, i)  #
                                    if url is not None and url.startswith("https://"):  # fixme: when it's http://
                                                                                        #  instead of
                                                                                        #  https://, an error occurs
                                                                                        #  regarding proxy environment
                                        img_urls.append(url)
                                    # print(ebody[i+9:end_index])
            except HTTPError as err:  # if an HTTP error occurs, just do not process that image and move on to the next
                if err.code < 600:
                    pass
                # if err.code == 404:  # if the form not found, just increment the counter and go to the next loop
                #     pass
                # elif err.code == 500:
                #     pass
                # elif err.code == 502:
                #     pass
                else:
                    raise
            except OSError:  # if an OSError occurs, just do not process that image and move on to the next
                pass
        if count % save_period == 0 and count != 0:  # save images periodically as it takes too much time to
                                                        # fetch all the images first and the save them into a folder
            img_urls = remove_duplicates(img_urls)
            save_img_to_folder(img_urls, folder)
            img_urls = []
        count += 1
    # img_urls = remove_duplicates(img_urls)
    return img_urls


# deal with non-ascii characters
def escape_ascii(email_body, start):
    extentions = ["png", "jpg"]
    end_index = email_body.find("\"", start + 9)  # +9 due to "img src=""
    ascii_start = email_body.rfind('/', start, end_index)
    encoded_url = email_body[start+9:ascii_start] + quote(email_body[ascii_start:end_index])
    if encoded_url[-3:] in extentions or encoded_url[-4:0] == "jpeg":  # ignore other file types such as .gif
        return encoded_url
    return None


# removes the same urls from the list
def remove_duplicates(images):
    return list(OrderedDict.fromkeys(images))


def save_img_to_folder(images, folder_path):
    counter = len(os.listdir(folder_path))
    for img_url in images:
        url = img_url.replace(" ", "")
        try:
            urlreq.urlretrieve(url, folder_path + "img-" + str(counter)+".jpg")
            counter += 1
        except HTTPError as err:  # if an HTTP error occurs during retrieving the image by its URL,
                                    # skip this image
            if err.code < 600:
                pass
            # elif err.code == 502:
            #     pass
            # elif err.code == 404:  # if the image is not found, just increment the counter and go to the next loop
            #     pass
            else:
                raise
        except (ConnectionError, TimeoutError):
            pass
        except URLError:
            pass
        except OSError:
            pass


class MyThread(threading.Thread):
    def __init__(self, form_ids, dpath, interval, thread_name):
        threading.Thread.__init__(self)
        self.form_ids = form_ids
        self.dpath = dpath
        self.interval = interval
        self.thread_name = thread_name

    def run(self):
        get_image_urls(self.form_ids, self.dpath, self.interval, self.thread_name)


if __name__ == '__main__':
    thread_form_ids = read_csv(fpath)
    t1_folder = '../Images-1/'
    t2_folder = '../Images-2/'
    t3_folder = '../Images-3/'
    t4_folder = '../Images-4/'

    # Create 4 threads to parallelize the process to fetch and save images. Otherwise, it would take 2-3 times
    # more time.
    thread1 = MyThread(thread_form_ids, t1_folder, [0, 100000], 1)
    thread2 = MyThread(thread_form_ids, t2_folder, [100000, 200000], 2)
    thread3 = MyThread(thread_form_ids, t3_folder, [200000, 300000], 3)
    thread4 = MyThread(thread_form_ids, t4_folder, [300000, 400000], 4)
    threads = [thread1, thread2, thread3, thread4]

    for t in threads:
        t.start()
    for t in threads:  # wait for all threads to finish their execution before terminating
        t.join()

    # save_img_to_folder(imgs, folder)
    print("--end--")
