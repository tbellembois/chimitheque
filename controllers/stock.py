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
# $Id: stock.py 194 2015-02-23 16:27:16Z tbellemb $
#
from chimitheque_logger import chimitheque_logger

mylogger = chimitheque_logger()


@auth.requires(auth.has_permission('create_sc') or
               auth.has_permission('admin'))
@auth.requires_login()
def update():
    mylogger.debug(message='request.vars:%s' % request.vars)
    stock_id = request.args(0)
    product_id = db(db.stock.id == stock_id).select(db.stock.product).first().product

    form = crud.update(db.stock,
                       stock_id,
                       next=URL(request.application,
                                'product',
                                'details_reload',
                                args=product_id))

    cache.ram.clear(regex='.*/product/details')

    return dict(product_id=product_id,
                form=form)
