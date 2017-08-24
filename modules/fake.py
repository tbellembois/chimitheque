# Dummy code to enable code completion in IDE's.
if 0:

    from gluon.html import *
    from gluon.validators import *
    from gluon.http import redirect, HTTP
    from gluon.sqlhtml import SQLFORM, SQLTABLE
    from gluon.compileapp import LOAD

    from gluon.globals import Request, Response, Session, current
    from gluon.cache import Cache
    from gluon.languages import translator
    from gluon.tools import Auth, Crud, Mail, Service, PluginManager
    from gluon.dal import DAL, Field
    from chimitheque_multiple_widget import CHIMITHEQUE_MULTIPLE_widget

    # API objects
    request = Request()
    response = Response()
    session = Session()
    cache = Cache(request)
    T = translator(request, 'fr')

    # Objects commonly defined in application model files
    # (names are conventions only -- not part of API)
    db = DAL()
    auth = Auth(db)
    crud = Crud(db)
    mail = Mail()
    service = Service()
    plugins = PluginManager()
    settings = {}