"""Reusable base entities."""

from base64 import b64decode


class FileName(str):  # noqa

    def __new__(self, value, **kw):  # noqa
        super().__new__(self, value.strip())

    def __init__(self, value: str, *, max=50) -> None:  # noqa
        length = len(self)
        assert length > 2, "The file name is too short; min: 3 characters."
        if max != 0:
            assert length <= max, f"The file name is too long; max: {max} characters."
        assert not self.endswith("."), "A file name must not end with a dot."
        assert "." in self, "A file name must have an extension."
        assert "/" not in self, "A file name must not contain a slash."

    @property
    def extension(self):  # noqa
        return self.split(".")[-1]

    @property
    def title(self):  # noqa
        return self[: -(len(self.extension) + 1)]


class UploadedFile:  # noqa
    def __init__(self, filename: str, payload: str) -> None:  # noqa
        self.byts: bytes = b64decode(payload)
        self.filename = FileName(filename)
