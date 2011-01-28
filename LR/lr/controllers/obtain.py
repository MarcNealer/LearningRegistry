#   Copyright 2011 Department of Defence

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import logging, urllib2, json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ObtainController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('obtain', 'obtain')

    def index(self, format='html'):
        """GET /obtain: All items in the collection"""
        url = 'http://localhost:5984/resource_data/_all_docs'
        response = urllib2.urlopen(url)
        return response.read()
        # url('obtain')
    def create(self):
        """POST /obtain: Create a new item"""
        data = json.loads(request.body)
        def get_key(key):
           return key['doc_ID']
        keys = map(get_key,data['request_IDs'])
        return_data = urllib2.urlopen('http://localhost:5984/resource_data/_all_docs?include_docs=true',json.dumps({'keys': keys}))
        return_data = json.load(return_data)
        def format(doc):
           return doc['doc']
        print return_data
	return_data = {'documents' : map(format,return_data['rows'])}
        return return_data
        # url('obtain')

    def new(self, format='html'):
        """GET /obtain/new: Form to create a new item"""
        # url('new_obtain')

    def update(self, id):
        """PUT /obtain/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('obtain', id=ID),
        #           method='put')
        # url('obtain', id=ID)

    def delete(self, id):
        """DELETE /obtain/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('obtain', id=ID),
        #           method='delete')
        # url('obtain', id=ID)

    def show(self, id, format='html'):
        """GET /obtain/id: Show a specific item"""
        url = 'http://localhost:5984/resource_data/'+id
        response = urllib2.urlopen(url)
        return response.read()
        # url('obtain', id=ID)

    def edit(self, id, format='html'):
        """GET /obtain/id/edit: Form to edit an existing item"""
        # url('edit_obtain', id=ID)
