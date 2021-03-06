import browserid, json, couchdb
import logging
import urlparse
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from lr.model.node_status import NodeStatusModel
from lr.model import NodeConnectivityModel,LRNode as sourceLRNode
log = logging.getLogger(__name__)
import uuid
import urllib2
import httplib
#initialize the couchDB server

appConfig = config['app_conf']

#Default couchdb server that use by all the models when none is provided.
defaultCouchServer =  couchdb.Server(appConfig['couchdb.url.dbadmin'])
user_model = appConfig['couchdb.db.users']
class NewauthController(BaseController):
    def __before__(self):
        response.headers['Content-Type'] = 'application/json;charset=utf-8'
    def __getDB__(self):
        try:
            defaultCouchServer.create(user_model)
        except Exception as ex:
            pass
            #log.exception(ex)
        return defaultCouchServer[user_model]
    def update(self):
         """
         creates a new User record in the couchdb db
         :return:
         """
         userDB=self.__getDB__()
         try:
             if 'password' in request.POST:
                 rec=userDB.save({'_id':"org.couchdb.user:" + request.POST['name'],
                                  'name':request.POST['name'],
                                  'roles':['browserid'],'type':'user','browserid':True,
                                  'password':request.POST['password'],
                                  'oauth':{'consumer_keys':{request.POST['name']:request.POST['consumer_key']},
                                           'tokens':{'node_sign_token':request.POST['node_sign_token']}}})
             else:
                 rec=userDB.save({'_id':"org.couchdb.user:" + request.POST['name'],
                                  'name':request.POST['name'],
                                  'roles':['browserid'],
                                  'type':'user',
                                  'browserid':True,
                                  'oauth':{'consumer_keys':{request.POST['name']:request.POST['consumer_key']},
                                           'tokens':{'node_sign_token':request.POST['node_sign_token']}}})
             return json.dumps(userDB[rec[0]])
         except:
             return json.dumps(userDB["org.couchdb.user:"+ request.POST['name']])



