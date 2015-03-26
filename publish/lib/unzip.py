
import os
from urlparse import urljoin
import shutil
import sys
import tempfile
import zipfile

import requests
from publish.lib.upload import Uploader
from publish.lib.helpers import download_file, create_hash_file

class Unzipper(object):

    def unzip(self, package):
        """ Processes each resource in the package, and possibly also
            adds more resources if we manage to extract some. """
        extra_resources = []

        self.uploader = Uploader("unzipped/{}".format(package['name']))

        updated_resources = []
        print " +", package['name']
        for resource in package['resources']:
            if not resource['format'] == 'ZIP':
                updated_resources.append(resource)
                continue

            updated_resources.append(resource)
            print "   +", resource['name']
            extract_zip_to = self.unzip_file(resource['url'])

            print "        + Processing files in ", extract_zip_to

            files = []
            for (dirpath, dirnames, filenames) in os.walk(extract_zip_to):
                files.extend( [os.path.join(dirpath,p) for p in filenames])

            for f in files:
                res = self.local_file_to_resource(f, resource)
                if res:
                    updated_resources.append(res)

            shutil.rmtree(extract_zip_to)
        package['resources'] = updated_resources

        self.uploader.close()
        if extra_resources:
            package['resources'].extend(extra_resources)

    def local_file_to_resource(self, local_file, parent_resource):
        print "Adding {} from {}".format(local_file, parent_resource['name'])
        if local_file.lower().endswith('.zip'):
            return None

        filename = local_file.split('/')[-1]
        parent_desc = parent_resource['description']
        if parent_desc == parent_resource['name']:
            parent_desc = ""
        description = u"(Extracted from {}) {}".format(parent_resource['name'], parent_desc)
        resource= {
            "description": description.replace('\u00a0', ' '),
            "name": filename,
            "format": filename.split('.')[-1].upper(),
        }


        hash_file = create_hash_file(local_file)
        try:
            url = self.uploader.upload(local_file)
            resource['url'] = url
        except Exception, e:
            print e
            return None

        os.unlink(hash_file)

        return resource


    def unzip_file(self, url):
        """
        Fetches a file from a url, unzips it and returns the folder
        where the files were unzipped
        """
        download_file_to, filename = tempfile.mkstemp()
        extract_zip_to = tempfile.mkdtemp()

        r = requests.get(url, stream=True)
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                os.write(download_file_to, chunk)

        os.close(download_file_to)

        zip = zipfile.ZipFile(filename)
        for info in zip.infolist():
            zip.extract(info.filename, extract_zip_to)
        zip.close()
        print "        + Extracted {} files".format(len(zip.infolist()))

        os.unlink(filename)
        return extract_zip_to
