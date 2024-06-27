"""Common Pyramid responses."""

from pyramid.httpexceptions import HTTPSeeOther

from kerno.web.pyramid.typing import PyramidRequest


def absolutify(url: str, request: PyramidRequest) -> str:
    """Make *url* rooted, so scheme_domain_port is respected."""
    if not url.startswith("http"):
        left = request.registry.settings["scheme_domain_port"].rstrip("/")
        right = url.lstrip("/")
        return "/".join((left, right))
    return url


def redirect(url: str, request: PyramidRequest, **kw) -> HTTPSeeOther:
    """Return a HTTPSeeOther, ensuring scheme_domain_port is respected."""
    return HTTPSeeOther(location=absolutify(url, request), **kw)


def content_disposition_value(file_name: str) -> str:
    """Return the value of a Content-Disposition HTTP header."""
    return 'attachment;filename="{}"'.format(file_name.replace('"', "_"))


def prepare_xlsx_download(response, file_title: str, payload: bytes):
    """Add stuff to *response* so it becomes a spreadsheet download."""
    response.headers["Content-Type"] = (
        "application/application/"
        "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.headers["Content-Disposition"] = content_disposition_value(
        "{}.xlsx".format(file_title)
    )
    response.body = payload
    return response
