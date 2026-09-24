"""Block base class and the YAML key -> class registry."""

from __future__ import annotations

from typing import Annotated, Any, ClassVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, ValidationError, ValidationInfo

from ..context import RenderContext

REGISTRY: dict[str, type[Block]] = {}


class Block(BaseModel):
    """A renderable element. In YAML it is written as a single-key mapping, e.g. `{text: ...}`."""

    model_config = ConfigDict(extra="forbid")

    key: ClassVar[str]
    # Field that receives the value when the block is written as a scalar, e.g. `text: "hello"`.
    shorthand: ClassVar[str | None] = None

    def render(self, ctx: RenderContext) -> None:
        raise NotImplementedError


def register(key: str):
    def decorator(cls: type[Block]) -> type[Block]:
        cls.key = key
        REGISTRY[key] = cls
        return cls

    return decorator


def parse_block(value: Any, context: dict[str, Any] | None = None) -> Block:
    if isinstance(value, Block):
        return value
    if not isinstance(value, dict) or len(value) != 1:
        raise ValueError(f"a block must be a mapping with exactly one of {sorted(REGISTRY)} as key")
    ((key, body),) = value.items()
    cls = REGISTRY.get(key)
    if cls is None:
        raise ValueError(f"unknown block {key!r}, expected one of {sorted(REGISTRY)}")
    if not isinstance(body, dict):
        if cls.shorthand is None:
            raise ValueError(f"{key!r} block needs a mapping")
        body = {cls.shorthand: body}
    try:
        return cls.model_validate(body, context=context)
    except ValidationError as e:
        details = "; ".join(
            f"{'.'.join(map(str, (key, *err['loc'])))}: {err['msg'].removeprefix('Value error, ')}" for err in e.errors()
        )
        raise ValueError(details) from None


def _validate_block(value: Any, info: ValidationInfo) -> Block:
    return parse_block(value, info.context)


AnyBlock = Annotated[Block, BeforeValidator(_validate_block)]
