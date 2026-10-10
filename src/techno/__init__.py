def main() -> None:
    """Run the command-line interface."""
    from .cli import main as cli_main

    cli_main()

__all__ = ["main"]
