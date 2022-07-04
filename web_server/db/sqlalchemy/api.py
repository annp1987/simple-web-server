"""SQLAlchemy storage backend."""

import threading

from oslo_config import cfg
from oslo_db import api as oslo_db_api
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log

from web_server.db import exceptions
from web_server.db.sqlalchemy import models


DEFAULT_FWG = 'default_fwg'
CONF = cfg.CONF
LOG = log.getLogger(__name__)
_CONTEXT = threading.local()

enginefacade.configure(
    sqlite_fk=True,
    max_retries=5,
    mysql_sql_mode='ANSI'
)

_BACKEND_MAPPING = {'sqlalchemy': 'web_server.db.sqlalchemy.api'}
IMPL = oslo_db_api.DBAPI.from_config(CONF, backend_mapping=_BACKEND_MAPPING, lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


def get_backend():
    """The backend is this module itself."""
    return Connection()


def _session_for_read():
    return enginefacade.reader.using(_CONTEXT)


# Please add @oslo_db_api.retry_on_deadlock decorator to all methods using
# _session_for_write (as deadlocks happen on write), so that oslo_db is able
# to retry in case of deadlocks.
def _session_for_write():
    return enginefacade.writer.using(_CONTEXT)


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    with _session_for_read() as session:
        query = session.query(model, *args, **kwargs)
        return query


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        err = 'The sort_key value "%(key)s" is an invalid field for sorting' % {'key': sort_key}
        raise exceptions.InvalidParameterValue(error=err)
    return query.all()


class Connection(object):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    @oslo_db_api.retry_on_deadlock
    def network_add(self, name, physical_network, network_type, segmentation_id, local_vlan):
        network = models.Network(
            name=name,
            physical_network=physical_network,
            network_type=network_type,
            segmentation_id=segmentation_id,
            local_vlan=local_vlan
        )
        with _session_for_write() as session:
            try:
                session.add(network)
                session.flush()
            except db_exc.DBDuplicateEntry:
                raise exceptions.DuplicateNetworkEntry(
                    net_type=network_type,
                    segment_id=segmentation_id,
                    local_vlan=local_vlan)
        return network
