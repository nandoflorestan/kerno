"""A complement to our email module, for those who use pyramid_mailer."""

from typing import Dict

from pyramid_mailer.message import Message

from kerno.email import EmailMessageBase


class EmailMessage(EmailMessageBase):
    """Abstract base class with methods that depend on pyramid_mailer."""

    def __init__(self, mailer_settings: Dict[str, str], **kw):
        """Constructor."""
        super().__init__(**kw)
        self.mailer_settings = mailer_settings

    def to_message(self) -> Message:
        """Convert this instance into a pyramid_mailer Message."""
        adict = self.to_dict()
        env = adict['envelope']
        return Message(
            subject=adict['subject'],
            html=adict['html'],
            body=adict['plain'],
            recipients=env['recipients'],
            sender=env['sender'] or self.mailer_settings["default_sender"],
            cc=env['cc'],
            bcc=env['bcc'],
            extra_headers={'reply_to': env['reply_to']},
        )
