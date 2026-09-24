from pathlib import Path

import click
import yaml
from pydantic import ValidationError

from . import load


@click.command(help="Render a YAML report to PDF.")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output PDF (default: <title>.pdf).",
)
@click.version_option(package_name="pdformy")
def main(source: Path, output: Path | None) -> None:
    try:
        report = load(source)
    except ValidationError as e:
        click.echo(f"{source}: invalid report", err=True)
        for err in e.errors():
            location = ".".join(map(str, err["loc"]))
            click.echo(f"  {location}: {err['msg'].removeprefix('Value error, ')}", err=True)
        raise SystemExit(1)
    except (yaml.YAMLError, ValueError) as e:
        raise click.ClickException(str(e))
    click.echo(report.build(output))
