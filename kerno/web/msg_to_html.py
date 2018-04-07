"""A registry for ways to convert an UIMessage to HTML code."""

from cgi import escape
import reg
# from kerno.state import UIMessage


# Dispatch depending on the value of *flavor*.
@reg.dispatch(reg.match_key('flavor', lambda flavor, msg, close: flavor))
# Cannot type-annotate this function, Reg 0.11 does not support it:
def msg_to_html(flavor, msg, close=True):
    """Render ``msg`` (an UIMessage instance) as HTML markup.

    Example usage in a Mako template::

        <div class="flash-messages">
            % for msg in request.session.pop_flash():
                ${msg_to_html(flavor='bootstrap3', msg=msg)|n}
            % endfor
        </div>

    Example usage in a Jinja2 template::

        {%- block flash -%}
            <div class="flash-messages">
                {%- for msg in request.session.pop_flash() -%}
                    {$ msg_to_html(flavor='bootstrap3', msg=msg) | safe $}
                {%- endfor -%}
            </div>
        {%- endblock -%}
    """
    raise NotImplementedError()


@msg_to_html.register(flavor='bootstrap3')
# Cannot type-annotate this function, Reg 0.11 does not support it:
def msg_to_bootstrap3(flavor, msg, close=True):
    """Render the UIMessage ``msg`` as bootstrap 3 compatible HTML.

    If using Pyramid you can store UIMessage instances as flash messages
    in the user's session, then use this to render them as bootstrap alerts.
    """
    return '<div class="alert alert-{kind}{cls} fade in">{close}' \
        '{body}</div>\n'.format(
            kind=escape(msg.kind),
            cls=' alert-block' if msg.html else '',
            close='<button type="button" class="close" data-dismiss="alert" '
                  'aria-label="Close"><span aria-hidden="true">×</span>'
                  '</button>' if close else '',
            body=msg.html or escape(msg.plain),
        )


def includeme(config):
    """Make ``msg_to_html()`` available to templates in Pyramid."""
    def before_rendering_template(event):
        event['msg_to_html'] = msg_to_html

    from pyramid.events import BeforeRender
    config.add_subscriber(before_rendering_template, BeforeRender)
