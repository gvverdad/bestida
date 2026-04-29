from sqlalchemy_continuum.plugins.base import Plugin


class UserPlugin(Plugin):
    def transaction_args(self, uow, session):
        # avoid circular import
        from ..security.policy import get_current_uid, get_request_client

        return {
            'user_id': get_current_uid(),
            'remote_addr': get_request_client()
        }
