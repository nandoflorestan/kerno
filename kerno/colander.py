"""Convenience to use colander with kerno."""

import colander as c

from kerno.state import MalbonaRezulto
from kerno.typing import DictStr

_ = str  # TODO add i18n


def validate_schema(
    schema: c.SchemaType,
    adict: DictStr,
    mal_title: str = _("Validation error"),
    mal_plain: str = _("The data do not pass server validation."),
) -> DictStr:
    """Conveniently validate a colander schema and return the clean dict.

    But if colander.Invalid is raised, put it inside a MalbonaRezulto.
    """
    try:
        return schema.deserialize(adict)
    except c.Invalid as e:
        malbona = MalbonaRezulto()
        malbona.add_toast(title=mal_title, plain=mal_plain)
        malbona.invalid = e.asdict()
        raise malbona


class NumLines:
    """Colander validator that checks the number of lines in text."""

    def __init__(
        self,
        min: int = 0,
        max: int = -1,
        min_err: str = "Not enough lines (minimum {min})",
        max_err: str = "Too many lines (maximum {max})",
    ) -> None:  # noqa
        self.min = min
        self.max = max
        self.min_err = min_err
        self.max_err = max_err

    def __call__(self, node, value) -> None:  # noqa
        num_lines = value.count("\n") + 1
        if self.min > 0 and num_lines < self.min:
            # err = _(self.min_err, mapping={"min": self.min})
            raise c.Invalid(node, self.min_err.format(min=self.min))
        if self.max > -1 and num_lines > self.max:
            # err = _(self.max_err, mapping={"max": self.max})
            raise c.Invalid(node, self.max_err.format(max=self.max))
