#!/usr/bin/env python3

import email
import os
import re
from urllib.parse import urlparse

def parser(base_dir, msg_type, verbose=False):
    labeled_messages = []

    for f in os.listdir(base_dir):
        filepath = os.path.join(base_dir, f)
        with open(filepath) as fp:
            try:
                b = email.message_from_file(fp)
                body = ""

                if b.is_multipart():
                    for part in b.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))

                        # skip any text/plain (txt) attachments
                        #if ctype == "text/plain" and "attachment" not in cdispo:
                        if ctype == "text/plain":

                            if msg_type == 1:
                                body = str(part.get_payload(decode=1).decode("utf-8"))
                            elif msg_type == 0:
                                body = str(part.get_payload(decode=0))

                            semi_cleaned = body.replace(
                                    "\n", " "
                                    ).replace(
                                    "\r", " "
                                    ).replace(
                                    "\xa0", " "
                                    ).replace(
                                    "\u200c", " "
                                    ).replace("\t", " ")
                            # God help me
                            purge_embedded_urls = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", semi_cleaned)
                            parsed_text = purge_embedded_urls
                            labeled_messages.append((msg_type, parsed_text))
                            break
                # not multipart - i.e. plain text, no attachments, keeping fingers crossed
                else:
                    body = b.get_payload(decode=True)
                    labeled_messages.append(msg_type, body)
            except Exception as e:
                if verbose:
                    print("Skipping " + filepath)
                    print(str(e))
    return labeled_messages

def detect_url(msg_type):
    detected_url = []
    domains = []

    for i in range(len(msg_type)):
        try:
            detected_url.append((re.search("(?P<url>https?://[^\s]+)", str(msg_type[i])).group("url")))
            domains.append([urlparse(detected_url[j]).netloc for j in range(len(detected_url))])
        except:
            pass

    return domains
