"""Helpers and sane defaults for usage of the Pydantic library."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, conint, constr

if TYPE_CHECKING:
    ReqStr = str
    EmptyStr = str
    ZeroOrMore = int
else:
    ReqStr = constr(min_length=1, strip_whitespace=True, strict=True)
    EmptyStr = constr(min_length=0, strip_whitespace=True, strict=True)
    ZeroOrMore = conint(gt=-1)


class Pydantic(BaseModel):
    """Base class for our validation models."""

    class Config:
        """Controls the behaviour of pydantic."""

        # https://pydantic-docs.helpmanual.io/usage/model_config/
        anystr_strip_whitespace = True
