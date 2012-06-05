'''
Created on Oct 11, 2011

@author: jklo
'''
from contextlib import closing
from functools import wraps
from ijson.parse import items
from pylons import config
from uuid import uuid1
import copy
import couchdb
import ijson
import json
import logging
import os
import time
import urllib, urlparse, oauth2
import urllib2

log = logging.getLogger(__name__)

class SetFlowControl(object):
    def __init__(self,enabled,serviceDoc):
        server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.nodeDb = server[config['couchdb.db.node']]
        self.enabled = enabled
        self.serviceDoc = serviceDoc
    def __call__(self,f):
        def set_flow_control(obj, *args, **kw):
            serviceDoc = self.nodeDb[self.serviceDoc]
            service_data = copy.deepcopy(serviceDoc['service_data'])     
            serviceDoc['service_data']['flow_control'] = self.enabled
            serviceDoc['service_data']['doc_limit'] = 100
            serviceDoc['service_data']['id_limit'] = 100
            self.nodeDb[self.serviceDoc] = serviceDoc
            try:
                f(obj, *args, **kw)
            finally:
                serviceDoc['service_data'] = service_data         
                self.nodeDb[self.serviceDoc] = serviceDoc  
        return set_flow_control
def ForceCouchDBIndexing():
    json_headers = {"Content-Type": "application/json"}
    couch = {
        "url": config["couchdb.url"],
        "resource_data": config["couchdb.db.resourcedata"]
    }

    def indexTestData(obj):
        
        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        design_docs = obj.db.view('_all_docs', **opts)
        for row in design_docs:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                for view in row.doc["views"].keys():
#                    view = row.doc["views"].keys()[0]
                    view_name = "{0}/_view/{1}".format( row.key, view)
                    index_opts = { "limit": 1, "descending": 'true'}
                    if "reduce" in row.doc["views"][view]:
                        index_opts["reduce"] = 'false'
                    # log.debug("Indexing: {0}".format( view_name))
                    req = urllib2.Request("{url}/{resource_data}/{view}?{opts}".format(view=view_name, opts=urllib.urlencode(index_opts), **couch), 
                                          headers=json_headers)
                    res = urllib2.urlopen(req)
#                    view_result = obj.db.view(view_name, **index_opts)
                    # log.error("Indexed: {0}, got back: {1}".format(view_name, json.dumps(res.read())))
            else:
                pass#log.error("Not Indexing: {0}".format( row.key))
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                indexTestData(self)
                fn(self, *args, **kw)
            except :
                raise
            finally:
                indexTestData(self)
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator




def PublishTestDocs(sourceData, prefix, sleep=0, force_index=True):
    
    json_headers = {"Content-Type": "application/json"}
    test_data_log = "test-data-%s.log" % prefix
    couch = {
        "url": config["couchdb.url"],
        "resource_data": config["couchdb.db.resourcedata"]
    }
    
    def writeTestData(obj):
        if not hasattr(obj, "test_data_ids"):
            obj.test_data_ids = {}
        
        obj.test_data_ids[prefix] = []
        with open(test_data_log, "w") as plog:
            for doc in sourceData:
                doc["doc_ID"] = prefix+str(uuid1())
                obj.app.post('/publish', params=json.dumps({"documents": [ doc ]}), headers=json_headers)
                plog.write(doc["doc_ID"] + os.linesep)
                obj.test_data_ids[prefix].append(doc["doc_ID"])
                if sleep > 0:
                    time.sleep(sleep)
    
    def indexTestData(obj):
        
        if force_index == False:
            return
        opts = {
                "startkey":"_design/",
                "endkey": "_design0",
                "include_docs": True
        }
        design_docs = obj.db.view('_all_docs', **opts)
        for row in design_docs:
            if "views" in row.doc and len(row.doc["views"].keys()) > 0:
                for view in row.doc["views"].keys():
#                    view = row.doc["views"].keys()[0]
                    view_name = "{0}/_view/{1}".format( row.key, view)
                    index_opts = { "limit": 1, "descending": 'true'}
                    if "reduce" in row.doc["views"][view]:
                        index_opts["reduce"] = 'false'
                    # log.error("Indexing: {0}".format( view_name))
                    req = urllib2.Request("{url}/{resource_data}/{view}?{opts}".format(view=view_name, opts=urllib.urlencode(index_opts), **couch), 
                                          headers=json_headers)
                    res = urllib2.urlopen(req)
#                    view_result = obj.db.view(view_name, **index_opts)
                    # log.error("Indexed: {0}, got back: {1}".format(view_name, json.dumps(res.read())))
            else:
                pass# log.error("Not Indexing: {0}".format( row.key))
    
    def cacheTestData(obj):
        req = urllib2.Request("{url}/{resource_data}/_all_docs?include_docs=true".format(**couch), 
                              data=json.dumps({"keys":obj.test_data_ids[prefix]}), 
                              headers=json_headers)
        res = urllib2.urlopen(req)
        docs = list(items(res, 'rows.item.doc'))
        
        if not hasattr(obj, "test_data_sorted"):
            obj.test_data_sorted = {}
            
        obj.test_data_sorted[prefix] = sorted(docs, key=lambda k: k['node_timestamp'])
        
        
        
    def removeTestData(obj):
        for doc_id in obj.test_data_ids[prefix]:
            try:
                del obj.db[doc_id]
            except Exception as e:
                print e.message
            try:
                del obj.db[doc_id+"-distributable"]
            except Exception as e:
                print e.message
        
        try:        
            del obj.test_data_ids[prefix]
        except Exception as e:
            print e.message
        
        try:
            del obj.test_data_ids[prefix]
        except Exception as e:
            print e.message
        
    
    def test_decorator(fn):
        def test_decorated(self, *args, **kw):
            try:
                #print "Wrapper Before...."
                writeTestData(self)
                indexTestData(self)
                cacheTestData(self)
                fn(self, *args, **kw)
            except :
                raise
            finally:
                removeTestData(self)
                indexTestData(self)
                #print "Wrapper After...."
                
        return test_decorated
    return test_decorator


def getExtraEnvironment(base_url=None):
    env = {}
    if base_url:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
        if query or fragment:
            raise ValueError(
                "base_url (%r) cannot have a query or fragment"
                % base_url)
        if scheme:
            env['wsgi.url_scheme'] = scheme
        if netloc:
            if ':' not in netloc:
                if scheme == 'http':
                    netloc += ':80'
                elif scheme == 'https':
                    netloc += ':443'
                else:
                    raise ValueError(
                        "Unknown scheme: %r" % scheme)
            host, port = netloc.split(':', 1)
            env['SERVER_PORT'] = port
            env['SERVER_NAME'] = host
            env['HTTP_HOST'] = netloc
        if path:
            env['SCRIPT_NAME'] = urllib.unquote(path)
    return env

class OAuthRequest(object):
    def __init__(self,  path, http_method="GET", url_base="http://www.example.com",  oauth_user_attrib="oauth_user", oauth_info_attrib="oauth" ):
        self.oauth_user_attrib = oauth_user_attrib
        self.oauth_info_attrib = oauth_info_attrib
        self.http_method = http_method
        self.url_base = url_base
        self.path = path
        self.server = couchdb.Server(config['couchdb.url.dbadmin'])
        self.users =  self.server[config['couchdb.db.users']] 

    def __call__(self, fn):

        def create_user(oauth_user):
            try:
                del self.users[oauth_user["_id"]]
            except:
                pass
            finally:
                self.users.save(oauth_user)

        def remove_user(oauth_user):
            try:
                del self.users[oauth_user["_id"]]
            except:
                pass

        @wraps(fn)
        def test_decorator(cls, *args, **kwargs):
            if (hasattr(cls, self.oauth_user_attrib)):
                self.oauth_user = getattr(cls, self.oauth_user_attrib)
            else:
                err = AttributeError()
                err.message = "Missing attribute '%s' which should be data for CouchDB OAuth User" % self.oauth_user_attrib
                raise  err

            consumer = oauth2.Consumer(key=self.oauth_user["name"], secret=self.oauth_user["oauth"]["consumer_keys"][self.oauth_user["name"]])
            token = oauth2.Token(key="node_sign_token", secret=self.oauth_user["oauth"]["tokens"]["node_sign_token"])

            params = {
                "oauth_signature_method": "HMAC-SHA1",
            }


            req = oauth2.Request.from_consumer_and_token(consumer, token, http_method=self.http_method, http_url="{0}{1}".format(self.url_base, self.path), parameters=params)

            # Sign the request.
            signature_method = oauth2.SignatureMethod_HMAC_SHA1()
            req.sign_request(signature_method, consumer, token)
            
            header = req.to_header()
            header["Authorization"] = str(header["Authorization"])

            extraEnv = getExtraEnvironment(self.url_base)

            class OauthInfo(object):
                def __init__(self, consumer, token, request, header, extraEnv, path):
                    self.consumer = consumer
                    self.token = token
                    self.request = request
                    self.header = header
                    self.env = extraEnv
                    self.path = path


            setattr(cls, self.oauth_info_attrib, OauthInfo(consumer, token, req, header, extraEnv, self.path))
    
            try:
                create_user(self.oauth_user)
                result = fn(cls, *args, **kwargs)
                return result
            finally:
                delattr(cls, self.oauth_info_attrib)
                remove_user(self.oauth_user)

        return test_decorator