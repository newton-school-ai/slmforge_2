"""SLMForge CLI entrypoint.

Subcommands are stubbed for M1. Real implementations land in M7.
"""

from __future__ import annotations

import typer

app = typer.Typer(no_args_is_help=True, help="SLMForge -- plug-and-play SLM builder.")


@app.command()
def init() -> None:
    """Initialise a .slmforge/ config directory in the current folder."""
    typer.echo("init: not yet implemented (M7)")


@app.command()
def build(
    auto: bool = typer.Option(False, "--auto", help="Skip all confirmation prompts."),
    recipe: str | None = typer.Option(None, "--recipe", help="Run a bundled recipe by name."),
) -> None:
    """Discover data in cwd, detect task, fine-tune, eval, and print usage doc."""
    typer.echo(f"build: not yet implemented (M7). auto={auto} recipe={recipe}")


@app.command()
def eval(build_id: str) -> None:  # noqa: A002
    """Re-run eval on an existing build."""
    typer.echo(f"eval: not yet implemented (M7). build_id={build_id}")


@app.command()
def serve(build_id: str, port: int = 8000) -> None:
    """Start a local vLLM endpoint for a build."""
    typer.echo(f"serve: not yet implemented (M7). build_id={build_id} port={port}")


@app.command(name="list")
def list_cmd() -> None:
    """List all builds in this folder."""
    typer.echo("list: not yet implemented (M7)")


@app.command()
def usage(build_id: str) -> None:
    """Print the USAGE.md for a build."""
    typer.echo(f"usage: not yet implemented (M7). build_id={build_id}")


@app.command()
def ui() -> None:
    """Launch the localhost web UI."""
    typer.echo("ui: not yet implemented (M7)")


data_app = typer.Typer(no_args_is_help=True, help="Manage datasets.")
app.add_typer(data_app, name="data")


@data_app.command()
def prefetch(dataset_id: str) -> None:
    """Prefetch a public Hugging Face dataset and cache it locally."""
    from slmforge.data import prefetch as data_prefetch

    try:
        cache_path = data_prefetch(dataset_id)
        typer.echo(cache_path)
    except Exception as e:
        typer.echo(f"Error prefetching dataset {dataset_id}: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
