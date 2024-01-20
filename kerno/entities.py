"""Reusable base entities."""

from base64 import b64decode


class FileName:  # noqa

    def __init__(self, value: str, *, max=50) -> None:  # noqa
        self.value = value.strip()
        length = len(self.value)
        assert length > 2, "The file name is too short; min: 3 characters."
        if max != 0:
            assert length <= max, f"The file name is too long; max: {max} characters."
        assert not self.value.endswith("."), "A file name must not end with a dot."
        assert "." in self.value, "A file name must have an extension."
        assert "/" not in self.value, "A file name must not contain a slash."

    @property
    def extension(self):  # noqa
        return self.value.split(".")[-1]

    @property
    def title(self):  # noqa
        return self.value[: -(len(self.extension) + 1)]

    def __str__(self):
        return self.value


class UploadedFile:  # noqa
    def __init__(self, filename: str, payload: str) -> None:  # noqa
        self.byts: bytes = b64decode(payload)
        self.filename = FileName(filename)
