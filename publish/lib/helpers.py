import requests
import requests_cache

def download_file(url, target_file):
    with requests_cache.disabled():
        r = requests.get(url, stream=True)
        with open(target_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return target_file