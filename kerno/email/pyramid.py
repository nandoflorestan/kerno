"""A complement to our email module, for those that use Pyramid."""

from bag.reify import reify
import premailer
from pyramid.renderers import render


class PyramidEmail:
    """Mixin that uses Pyramid to render the HTML template."""

    @reify
    def html(self):
        """Return the rich text version of the email message."""
        html = render(self.HTML_TEMPLATE, self.adict)
        return premailer.transform(html)  # Inline CSS styles
