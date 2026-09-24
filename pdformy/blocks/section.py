from __future__ import annotations

from ..context import RenderContext
from .base import AnyBlock, Block
from .heading import Subtitle, Title


class Section(Block):
    """A titled node of the report tree: its content blocks, then its child sections."""

    title: str
    subtitle: str | None = None
    content: list[AnyBlock] = []
    sections: list[Section] = []

    def render(self, ctx: RenderContext) -> None:
        label = self.title
        if ctx.theme.numbered and ctx.number:
            label = f"{'.'.join(map(str, ctx.number))}  {label}"
        Title(text=label, level=ctx.level).render(ctx)
        if self.subtitle:
            Subtitle(text=self.subtitle).render(ctx)
        for block in self.content:
            block.render(ctx)
        for index, section in enumerate(self.sections, start=1):
            section.render(ctx.child(index))
