import hashlib
import html2text
import os
import requests
import requests_cache

def filename_for_resource(resource):
    hashed = hashlib.md5(resource['url']).hexdigest()
    return "{}.{}".format(hashed, resource.get('format', 'bin').lower())

def download_file(url, target_file):
    with requests_cache.disabled():
        size = 0
        print "- Fetching url: {}".format(url)

        if os.environ.get('REQ_DEV') == "1":
            if os.path.exists(target_file):
                print "-- Exists, not fetching"
                return target_file


        r = requests.get(url, stream=True)
        if r.status_code > 500:
            raise IOError("Failed to get a response from the server")

        m = hashlib.md5()

        with open(target_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    size += len(chunk)

                    f.write(chunk)
                    m.update(chunk)

                    f.flush()

        print "-- Wrote {} bytes".format(size)

        print target_file
        hashfile = open("{}.hash".format(target_file), "wb")
        hashfile.write(m.hexdigest())
        hashfile.close()
        return target_file


def remove_tables_from_dom(dom):
    for bad in dom.xpath("//table"):
        bad.getparent().remove(bad)

def to_markdown(text):
    return html2text.html2text(text.decode('latin-1'))
