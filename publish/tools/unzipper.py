#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This tool is used to find .zip files on a CKAN instance and then:

    1. Pull the .zip
    2. Extract the contents
    3. Re-upload as new resources if they themselves are not .zips
    4. Delete the original .zip

'''
import ConfigParser

import ckanapi
import ffs
import requests
import requests_cache

from publish.lib.unzip import Unzipper


config = ConfigParser.ConfigParser()
config.read(ffs.Path('~/.dc.ini').abspath)

TEST = {"origin": "http://systems.hscic.gov.uk/data/ods/datadownloads/monthamend", "license_title": "UK Open Government Licence (OGL)", "maintainer": "", "relationships_as_object": [], "private": False, "maintainer_email": "", "num_tags": 2, "frequency": [], "id": "afb0f543-8346-4bfe-9f08-597346429f50", "metadata_created": "2015-03-02T16:29:01.990722", "metadata_modified": "2015-03-23T11:05:12.581363", "author": "", "author_email": "", "state": "active", "version": "", "license_id": "uk-ogl", "type": "dataset", "resources": [{"resource_group_id": "44b84607-ffe7-41f4-901c-a2b7eac55b84", "cache_last_updated": "", "revision_timestamp": "2015-03-12T16:05:26.161335", "webstore_last_updated": "", "datastore_active": False, "id": "18bdfe5b-7f58-4f61-a34f-d9ca955e4e69", "size": "", "state": "active", "hash": "", "description": "Changes to Organisation Details: eamendam.zip", "format": "ZIP", "tracking_summary": {"total": 0, "recent": 0}, "last_modified": "", "url_type": "", "mimetype": "", "cache_url": "", "name": "eamendam.zip", "created": "2015-03-02T16:29:02.354137", "url": "https://nhsenglandfilestore.s3.amazonaws.com/ods/eamendam.zip", "webstore_url": "", "mimetype_inner": "", "position": 0, "revision_id": "ed987348-bc94-4e70-bb63-46bc5a325a33", "resource_type": ""}, {"resource_group_id": "44b84607-ffe7-41f4-901c-a2b7eac55b84", "cache_last_updated": "", "revision_timestamp": "2015-03-12T16:05:26.991390", "webstore_last_updated": "", "datastore_active": False, "id": "c1d7ffe6-e093-487f-88ad-80e92951d02c", "size": "", "state": "active", "hash": "", "description": "Changes to GP and\u00a0GP Practice data: egpam.zip", "format": "ZIP", "tracking_summary": {"total": 0, "recent": 0}, "last_modified": "", "url_type": "", "mimetype": "", "cache_url": "", "name": "egpam.zip", "created": "2015-03-02T16:29:02.686038", "url": "https://nhsenglandfilestore.s3.amazonaws.com/ods/egpam.zip", "webstore_url": "", "mimetype_inner": "", "position": 1, "revision_id": "0c1e8701-e338-46e3-81d7-a76ef7068c3e", "resource_type": ""}, {"resource_group_id": "44b84607-ffe7-41f4-901c-a2b7eac55b84", "cache_last_updated": "", "revision_timestamp": "2015-03-12T16:05:27.899765", "webstore_last_updated": "", "datastore_active": False, "id": "0944571d-664d-4c64-927b-a063769bf602", "size": "", "state": "active", "hash": "", "description": "Changes to GP Practice and\u00a0PCO Membership data: egpmemam.zip", "format": "ZIP", "tracking_summary": {"total": 0, "recent": 0}, "last_modified": "", "url_type": "", "mimetype": "", "cache_url": "", "name": "egpmemam.zip", "created": "2015-03-02T16:29:03.051019", "url": "https://nhsenglandfilestore.s3.amazonaws.com/ods/egpmemam.zip", "webstore_url": "", "mimetype_inner": "", "position": 2, "revision_id": "7fff5645-416d-4580-a804-b1011c24ee26", "resource_type": ""}, {"resource_group_id": "44b84607-ffe7-41f4-901c-a2b7eac55b84", "cache_last_updated": "", "revision_timestamp": "2015-03-12T16:05:28.772437", "webstore_last_updated": "", "datastore_active": False, "id": "0a4daaef-6c1a-4a77-8190-ceac7b45e10e", "size": "", "state": "active", "hash": "", "description": "Changes to Private Controlled Drug Prescribers: epcdpam.zip", "format": "ZIP", "tracking_summary": {"total": 0, "recent": 0}, "last_modified": "", "url_type": "", "mimetype": "", "cache_url": "", "name": "epcdpam.zip", "created": "2015-03-02T16:29:03.482104", "url": "https://nhsenglandfilestore.s3.amazonaws.com/ods/epcdpam.zip", "webstore_url": "", "mimetype_inner": "", "position": 3, "revision_id": "a677f901-6828-4e2e-a586-45d23ce30404", "resource_type": ""}], "num_resources": 4, "coverage_end_date": "",
"tracking_summary": {"total": 0, "recent": 0}, "groups": [{"display_name": "ODS", "description": "ODS Datasets", "image_display_url": "", "title": "ODS", "id": "f088c845-63d8-4aff-b30a-dddcdeb003d5", "name": "ods"}], "creator_user_id": "729b5c32-ab5d-4260-a1b7-b7c0ddb9f180", "relationships_as_subject": [], "revision_timestamp": "2015-03-23T11:05:12.580414", "organization": {"description": "The national provider of information, data and IT systems for health and social care.", "created": "2014-10-27T16:08:10.376328", "title": "hscic", "name": "hscic", "revision_timestamp": "2015-01-06T14:16:19.552065", "is_organization": True, "state": "active", "image_url": "http://www.hscic.gov.uk/hscic/images/toplogo.gif", "revision_id": "2fc7e540-fe5e-40e4-8c2e-e2ec08e8819e", "type": "organization", "id": "d3f093ab-b8a1-4d3f-bf84-901d7cb0482b", "approval_status": "approved"}, "name": "ods-march-2014-monthly-amendments", "isopen": True, "url": "", "notes": "\n\n", "owner_org": "hscic", "license_url": "http://reference.data.gov.uk/id/open-government-licence", "title": "ODS - March\u00a02014 Monthly Amendments", "revision_id": "720b9254-34ee-4d13-a3f9-50ba67fd2734", "coverage_start_date": ""}


def main():
    requests_cache.install_cache('unzipper_cache', expire_after=82400)

    print "Server is ", config.get('ckan', 'url')
    ckan = ckanapi.RemoteCKAN(config.get('ckan', 'url'),
                              apikey=config.get('ckan', 'api_key'))

    package = ckan.action.package_show(id='ods-hospital-consultants')
    unzipper = Unzipper(ckan, config.get('ckan', 'url'))
    unzipper.unzip(package)

    ckan.action.package_update(**package)