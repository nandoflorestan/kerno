"""A registry for ways to convert an UIMessage to HTML code."""

from html import escape
from typing import List

import reg
from kerno.state import UIMessage
from kerno.web.pyramid.typing import KRequest


# Dispatch depending on the value of *flavor*.
@reg.dispatch(reg.match_key("flavor", lambda flavor, msg, close: flavor))
# Cannot type-annotate this function, Reg 0.11 does not support it:
def msg_to_html(flavor, msg, close=True):
    """Render ``msg`` (an UIMessage instance) as HTML markup.

    Example usage in a Mako template::

        <div class="flash-messages">
            % for msg in request.session.get_flash_msgs():
                ${msg_to_html(flavor='bootstrap3', msg=msg)|n}
            % endfor
        </div>

    Example usage in a Jinja2 template::

        {%- block flash -%}
            <div class="flash-messages">
                {%- for msg in request.session.get_flash_msgs() -%}
                    {$ msg_to_html(flavor='bootstrap3', msg=msg) | safe $}
                {%- endfor -%}
            </div>
        {%- endblock -%}
    """
    raise NotImplementedError()


@msg_to_html.register(flavor="bootstrap3")
# Cannot type-annotate this function, Reg 0.11 does not support it:
def msg_to_bootstrap3(flavor: str, msg: UIMessage, close: bool = True):
    """Render the UIMessage ``msg`` as bootstrap 3 compatible HTML.

    If using Pyramid you can store UIMessage instances as flash messages
    in the user's session, then use this to render them as bootstrap alerts.
    """
    return (
        '<div class="alert alert-{level}{cls} fade in">{close}'
        "{body}</div>\n".format(
            level=escape(msg.level),
            cls=" alert-block" if msg.html else "",
            close='<button type="button" class="close" data-dismiss="alert" '
            'aria-label="Close"><span aria-hidden="true">×</span>'
            "</button>"
            if close
            else "",
            body=msg.html or escape(msg.plain),
        )
    )


def includeme(config) -> None:  # noqa
    """Make request methods available in Pyramid."""

    def before_rendering_template(event):
        event["msg_to_html"] = msg_to_html

    from pyramid.events import BeforeRender

    config.add_subscriber(before_rendering_template, BeforeRender)
    config.add_request_method(add_flash, "add_flash")
    config.add_request_method(get_flash_msgs, "get_flash_msgs")


def add_flash(
    request: KRequest, allow_duplicate: bool = False, **kw
) -> UIMessage:
    """Add a flash message to the user's session. For convenience."""
    msg = UIMessage(**kw)
    request.session.flash(msg.to_dict(), allow_duplicate=allow_duplicate)
    return msg


def get_flash_msgs(request: KRequest) -> List[UIMessage]:
    """Return the UIMessages currently stored in the HTTP session."""
    return [UIMessage.from_payload(f) for f in request.session.pop_flash()]
