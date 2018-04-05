"""A registry for ways to convert an UIMessage to HTML code."""

from cgi import escape
import reg
from kerno.state import UIMessage


# Dispatch depending on the value of *flavor*.
@reg.dispatch(reg.match_key('flavor', lambda obj, flavor, **kw: flavor))
# Cannot type-annotate this function, Reg 0.11 does not support it:
def msg_to_html(flavor: str, msg: UIMessage, close: bool=True) -> str:
    """Render ``msg`` (an UIMessage instance) as HTML code."""
    raise NotImplementedError()


@msg_to_html.register(flavor='bootstrap3')
def msg_to_bootstrap3(flavor: str, msg: UIMessage, close: bool=True) -> str:
    """Render the UIMessage ``msg`` as bootstrap 3 compatible HTML."""
    return '<div class="alert alert-{kind}{cls} fade in">{close}' \
        '{body}</div>\n'.format(
            kind=escape(msg.kind),
            cls=' alert-block' if msg.html else '',
            close='<button type="button" class="close" data-dismiss="alert" '
                  'aria-label="Close"><span aria-hidden="true">×</span>'
                  '</button>' if close else '',
            body=msg.html or escape(msg.plain),
        )
