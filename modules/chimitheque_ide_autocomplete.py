# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id: chimitheque_ide_autocomplete.py 194 2015-02-23 16:27:16Z tbellemb $
# -*- coding: utf-8 -*-
if False:
    #
    # never imported - just for IDE autocompletion
    #
    from gluon import DAL; db = DAL()
    from gluon import settings
    from gluon.cache import Cache
    from gluon.dal import Field
    from gluon.globals import Request; request = Request()
    from gluon.globals import Response; response = Response()
    from gluon.globals import Session; session = Session()
    from gluon.html import *
    from gluon.http import HTTP
    from gluon.http import redirect
    from gluon.languages import translator; T = translator(request)
    from gluon.sqlhtml import SQLFORM
    from gluon.tools import Auth; auth = Auth()
    from gluon.tools import Crud, Mail
    from gluon.validators import *
    import sys
    mail = Mail()
    cache = Cache()
    crud = Crud(globals(), db)