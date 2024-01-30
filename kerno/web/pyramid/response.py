"""Common Pyramid response kinds."""


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
