# -*- coding: utf-8; -*-
#
# (c) 2011-2015 Thomas Bellembois thomas.bellembois@ens-lyon.fr
#
# This file is part of Chimithèque.
#
# Chimithèque is free software; you can redistribute it and/or modify
# it under the terms of the Cecill as published by the CEA, CNRS and INRIA
# either version 2 of the License, or (at your option) any later version.
#
# Chimithèque is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Cecill along with Chimithèque.
# If not, see <http://www.cecill.info/licences/>.
#
# SVN Revision:
# -------------
# $Id: default.py 202 2015-03-05 12:33:04Z tbellemb $
#
import os
from chimitheque_logger import chimitheque_logger

from fake import *

mylogger = chimitheque_logger()


@auth.requires_login()
def console():
    return mylogger.ram()


def index():
    """Default page."""
    redirect(URL(r=request, c='product', f='search', vars={}))


def user():
    mylogger.debug(message='--> default/user')
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if 'profile' in request.args:
        mylogger.debug(message='profile')
        redirect(URL(r=request, c='user', f='profile', vars={}))

    return dict(form=auth())


def download():
    """Allows downloading of uploaded files.
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """Exposes services.
    for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


def handle_error():
    """Custom error handler that returns correct status codes."""
    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket

    if not settings['error_mail_enable']:
        return '<html><body><h1>Internal error</h1>Ticket issued: <a href="/admin/default/ticket/%(ticket)s" target="_blank">%(ticket)s</a></body></html>' % {'ticket': ticket}

    if code is not None and request_url != request.url:	 # Make sure error url is not current url to avoid infinite loop.
        response.status = int(code)  # Assign the error status code to the current response. (Must be integer to work.)

    if code == '403':
        return "Not authorized"
    elif code == '404':
        return "Not found"
    elif code == '500':
        if settings['error_mail_enable']:

            _ticket_path = os.path.join(request.folder, 'errors', ticket.split('/')[1])
            _message = 'version: %(version)s - release_date: %(release_date)s' % {'version': settings['app_version'],
                                                                                  'release_date': settings['release_date']}

            attachment = Mail.Attachment(_ticket_path, content_type='text/plain')

            # Email a notice, etc:
            mail.send(to=[settings['error_mail_recipient']],
                      subject="Chimithèque error - %s" % settings['organization'],
                      attachments=attachment,
                      message=_message)

        return "Server error"
    else:
        return "Other error"
