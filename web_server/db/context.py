from oslo_context import context


class RequestContext(context.RequestContext):
    """Extends security contexts from the oslo.context library."""

    def __init__(self, is_public_api=False, **kwargs):
        """Initialize the RequestContext

        :param is_public_api: Specifies whether the request should be processed
            without authentication.
        :param kwargs: additional arguments passed to oslo.context.
        """
        super(RequestContext, self).__init__(**kwargs)
        self.is_public_api = is_public_api

    def to_policy_values(self):
        policy_values = super(RequestContext, self).to_policy_values()
        policy_values.update({
            'project_name': self.project_name,
            'is_public_api': self.is_public_api,
        })
        return policy_values

    def ensure_thread_contain_context(self):
        """Ensure threading contains context

        For async/periodic tasks, the context of local thread is missing.
        Set it with request context and this is useful to log the request_id
        in log messages.

        """
        if context.get_current():
            return
        self.update_store()


def get_admin_context():
    """Create an administrator context."""

    context = RequestContext(auth_token=None,
                             project_id=None,
                             overwrite=False)
    return context
