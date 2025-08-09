from __future__ import annotations

from typing import Any

from pydantic import BaseModel as _PydanticBaseModel
from pydantic import ConfigDict


def to_camel(snake_str: str) -> str:
    parts = snake_str.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


class BaseModel(_PydanticBaseModel):
    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
    )

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault("by_alias", True)
        return super().model_dump(*args, **kwargs)

