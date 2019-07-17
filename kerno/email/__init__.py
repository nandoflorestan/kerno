"""Extensible scheme for an app to send out email messages.

We provide only a well-structured API to build messages, such that
classes representing individual email messages are easy to change
and easy to test. And any backend capable of actually sending out
emails can be plugged at the end.
"""

from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple, Union

from bag.email_validator import EmailValidator
from bag.reify import reify
from bs4 import BeautifulSoup

from kerno.typing import DictStr


class EmailAddress:
    """Represents an email address, optionally with the person's name."""

    email_validator = EmailValidator()

    def __init__(self, email: str, name: str = ''):
        """Validate *email* and instantiate."""
        self.email_validator.validate_or_raise(email)
        self.email = email
        self.name = name

    def to_mailer(self) -> Union[str, Tuple[str, str]]:
        """Return either email or a 2-tuple (name, email)."""
        return (self.name, self.email) if self.name else self.email

    def __str__(self) -> str:
        return f'"{self.name}" <{self.email}>' if self.name else self.email


class Envelope:
    """Represents the envelope of an email message."""

    def __init__(  # noqa
        self, recipients: List[EmailAddress],
        cc: Optional[List[EmailAddress]] = None,
        bcc: Optional[List[EmailAddress]] = None,
        reply_to: Optional[EmailAddress] = None,
        sender: Optional[EmailAddress] = None,
    ):
        assert recipients
        self.recipients = recipients
        self.cc = cc or []
        self.bcc = bcc or []
        self.reply_to = reply_to
        self.sender = sender

    def to_dict(self) -> DictStr:
        """Return a dict with Python primitive types within."""
        return {
            'recipients': [str(r) for r in self.recipients],
            'cc': [str(r) for r in self.cc],
            'bcc': [str(r) for r in self.bcc],
            'reply_to': str(self.reply_to) if self.reply_to else None,
            'sender': str(self.sender) if self.sender else None,
        }


class EmailMessageBase(metaclass=ABCMeta):
    """Abstract base class to build an email message from templates.

    The plain text version is automatically built from the HTML version.

    Subclasses should declare certain static variables::

        class ACertainEmailMessage(EmailMessageBase):

            SUBJECT = 'Life or death matter in {app_name}!!!1'
            HTML_TEMPLATE = 'path/to/template.jinja2'
    """

    def __init__(self, adict: DictStr, envelope: Envelope):
        """:param adict: dictionary for use in templates."""
        self.adict = adict
        self.envelope = envelope

    @reify
    def subject(self) -> str:
        """May be overridden in subclasses to decorate the subject line."""
        return self.SUBJECT.format(**self.adict)  # type: ignore

    @reify
    @abstractmethod
    def html(self) -> str:
        """Must be overridden in subclasses to return the HTML version.

        Usually based on HTML_TEMPLATE. Example implementation::

            @reify
            def rich(self):
                return jinja2.get_template(
                    self.HTML_TEMPLATE).render(self.adict)
        """
        raise NotImplementedError()

    @reify
    def plain(self) -> str:
        """Autogenerate the plain text version from the rich version."""
        return BeautifulSoup(self.html, 'html.parser').get_text()

    def to_dict(self) -> DictStr:
        """Return a dict containing the computed parts of this message."""
        assert self.subject
        assert self.plain or self.html
        return {
            'envelope': self.envelope.to_dict(),
            'subject': self.subject,
            'html': self.html,
            'plain': self.plain,
        }
