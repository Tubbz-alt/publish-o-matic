import hashlib
import html2text
import os
import requests
import requests_cache

def download_file(url, target_file):
    with requests_cache.disabled():
        size = 0
        print "Fetching url: {}".format(url)

        if os.environ.get('REQ_DEV') == "1":
            print "Checking if file exists"
            if os.path.exists(target_file):
                print "Skipping"
                return target_file
            print "Doesn't exist - fetching"

        r = requests.get(url, stream=True)
        if r.status_code > 500:
            raise IOError("Failed to get a response from the server")
        with open(target_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    size += len(chunk)
                    f.write(chunk)
                    f.flush()
        print "Wrote {} bytes".format(size)
        return target_file


def remove_tables_from_dom(dom):
    for bad in dom.xpath("//table"):
        bad.getparent().remove(bad)

def to_markdown(text):
    return html2text.html2text(text.decode('latin-1'))
