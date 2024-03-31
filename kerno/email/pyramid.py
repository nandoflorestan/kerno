"""A complement to our email module, for those that use Pyramid."""

from bag.reify import reify

# 2023-08: libraries lack py.typed
import premailer  # type: ignore[import]
from pyramid.renderers import render  # type: ignore[import]


class PyramidEmail:
    """Mixin that uses Pyramid to render the HTML template."""

    @reify
    def html(self):
        """Return the rich text version of the email message."""
        html = render(self.HTML_TEMPLATE, self.adict)
        return premailer.transform(html)  # Inline CSS styles
