import eventlet
from eventlet import wsgi
from paste.deploy import loadapp
import routes
import routes.middleware as middleware
import webob.dec
import webob.exc


class Resource(object):
    def __init__(self, controller):
        self.controller = controller()

    @webob.dec.wsgify
    def __call__(self, req):
        match = req.environ['wsgiorg.routing_args'][1]
        action = match['action']
        if hasattr(self.controller, action):
            method = getattr(self.controller, action)
            print("request ", req)
            return method(req)
        return webob.exc.HTTPNotFound()


class Controller(object):

    def index(self, req):
        return 'List.'

    def create(self, req):
        return 'create'

    def delete(self, req):
        return 'delete'

    def update(self, req):
        return 'update'
    
    def show(self, req):
        return 'show'


class Application(object):
    def __init__(self):
        self.mapper = routes.Mapper()
        self.mapper.resource('app1', 'app1s', controller=Resource(Controller))
        self.router = middleware.RoutesMiddleware(self.dispatch, self.mapper)

    @webob.dec.wsgify
    def __call__(self, req):
        return self.router

    @classmethod
    def factory(cls, global_conf, **local_conf):
        return cls()

    @staticmethod
    @webob.dec.wsgify
    def dispatch(req):
        match = req.environ['wsgiorg.routing_args'][1]
        return match['controller'] if match else  webob.exc.HTTPNotFound()


class AuthMiddleware(object):
    def __init__(self, application):
        self.application = application

    @webob.dec.wsgify
    def __call__(self, req):
        if req.headers.get('X-Auth-Token') != "annp":
            return webob.exc.HTTPForbidden()
        return req.get_response(self.application)

    @classmethod
    def factory(cls, global_conf, **local_conf):
        def _factory(application):
            return cls(application)
        return _factory

def main():
    application = loadapp('config:/usr/local/etc/simple-web-server/config.ini')
    server = eventlet.spawn(wsgi.server,
                            eventlet.listen(('', 8080)), application)
    server.wait()

if '__main__' == __name__:
    main()
