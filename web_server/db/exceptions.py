from oslo_utils import excutils


class OvsException(Exception):
    """Base Ovs Exception.

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        try:
            super().__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:
            with excutils.save_and_reraise_exception() as ctxt:
                if not self.use_fatal_exceptions():
                    ctxt.reraise = False
                    # at least get the core message out if something happened
                    super().__init__(self.message)

    def __str__(self):
        return self.msg

    def as_dict(self):
        return {'error': self.msg}

    def use_fatal_exceptions(self):
        """Is the instance using fatal exceptions.

        :returns: Always returns False.
        """


class Conflict(OvsException):
    """A generic conflict exception."""
    pass


class InvalidParameterValue(OvsException):
    message = "Invalid parameter value %(error)s"


class DuplicateNetworkEntry(Conflict):
    message = "Duplicate network type=%(net_type)s segment_id=%(segment_id)s local_vlan=%(local_vlan)s entry"


class DatabaseVersionTooOld(OvsException):
    message = "Database version is too old"
