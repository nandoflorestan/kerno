"""Convenience to use colander with kerno."""

import colander as c

from kerno.state import MalbonaRezulto
from kerno.typing import DictStr

_ = str  # TODO add i18n


def validate_schema(
    schema: c.SchemaType,
    adict: DictStr,
    mal_title: str = _("Validation error"),
    mal_plain: str = _("The data does not pass server validation."),
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
