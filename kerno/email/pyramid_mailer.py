"""A complement to our email module, for those who use pyramid_mailer."""

# 2023-08: pyramid_mailer lacks py.typed
from pyramid_mailer.message import Message  # type: ignore[import]

from kerno.email import EmailMessageBase
from kerno.typing import DictStr


class EmailMessage(EmailMessageBase):
    """Abstract base class with methods that depend on pyramid_mailer."""

    def __init__(self, mailer_settings: dict[str, str], **kw):  # noqa
        super().__init__(**kw)
        self.mailer_settings = mailer_settings

    def to_message_args(self) -> DictStr:
        """Convert this into a dict to instantiate a pyramid_mailer Message.

        This is useful because Celery likes to use JSON serialization.
        """
        adict = self.to_dict()
        env = adict["envelope"]
        args = {
            "subject": adict["subject"],
            "html": adict["html"],
            "body": adict["plain"],
            "recipients": env["recipients"],
            "sender": env["sender"] or self.mailer_settings["default_sender"],
            "cc": env["cc"],
            "bcc": env["bcc"],
        }
        if env["reply_to"]:
            args["extra_headers"] = (("Reply-To", env["reply_to"]),)
        return args

    def to_message(self) -> Message:
        """Convert this instance into a pyramid_mailer Message."""
        margs = self.to_message_args()
        return Message(**margs)
