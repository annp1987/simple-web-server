from oslo_db.sqlalchemy import models
from urllib import parse as urlparse
from oslo_db import options as db_options
from oslo_config import cfg

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from web_server.db import consts

from oslo_utils import uuidutils
import datetime

CONF = cfg.CONF

db_options.set_defaults(CONF, connection='sqlite:////tmp/ovs_firewall.db')


def table_args():
    engine_name = urlparse.urlparse(CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class OvsFirewallBase(models.TimestampMixin, models.ModelBase):

    metadata = None

    version = Column(String(15), nullable=True, default='1.0')

    def as_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(
                getattr(self, column.name), (datetime.datetime, datetime.date)
            )
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


Base = declarative_base(cls=OvsFirewallBase)


class Network(Base):
    """Storing provider network"""
    __tablename__ = "networks"

    id = Column(String(consts.UUID_FIELD_SIZE), primary_key=True, default=uuidutils.generate_uuid())
    name = Column(String(255), unique=True)
    physical_network = Column(String(255))
    network_type = Column(String(40))
    segmentation_id = Column(Integer, unique=True)
    local_vlan = Column(Integer)

    def __init__(self, name, physical_network, network_type, segmentation_id, local_vlan):
        self.name = name
        self.id = uuidutils.generate_uuid()
        self.physical_network = physical_network
        self.network_type = network_type
        self.segmentation_id = segmentation_id
        self.local_vlan = local_vlan
