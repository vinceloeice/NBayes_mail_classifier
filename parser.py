#!/usr/bin/env python3

import email
import os
import re

source_ham = [
    ('dawcy/studencka'),
]

source_spam = [
    ('dawcy/oferty'),
]

detect_url = []

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
                        cdispo = str(part.get('Content-Disposition'))

                        # skip any text/plain (txt) attachments
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            body = str(part.get_payload(decode=True).decode('utf-8'))
                            semi_cleaned = body.replace('\n', ' '
                                                        ).replace(
                                                                '\r', ' '
                                                        ).replace(
                                                                u'\xa0', u' '
                                                        ).replace(
                                                                u'\u200c', u' '
                                                        ).replace(
                                                                '\t', ' '
                                                        )
                            detect_url.append((re.search("(?P<url>https?://[^\s]+)", semi_cleaned).group("url")))
                            parsed_text = semi_cleaned
                            labeled_messages.append((msg_type, parsed_text))
                            break
                # not multipart - i.e. plain text, no attachments, keeping fingers crossed
                else:
                    body = b.get_payload(decode=True)
                    labeled_messages.append(msg_type, body)
            except Exception as e:
                if verbose:
                    print('Skipping ' + filepath)
                    print(str(e))
    return labeled_messages

ham = parser(source_ham[0], 0)
spam = parser(source_spam[0], 1)
