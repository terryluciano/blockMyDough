from typing import Annotated

import typer

block_app = typer.Typer(help='Set a block timer for a preset', no_args_is_help=True)


@block_app.callback(invoke_without_command=True)
def block(
	ctx: typer.Context,
	name: Annotated[str, typer.Argument(help="Name of preset you'd like to block")],
	duration: Annotated[int, typer.Option('--dur', '-d', help='Duration in minutes')] = 25,
):
	"""Block a preset for a specified duration."""
	if ctx.invoked_subcommand is None and name is not None:
		print(f'Blocking {name} for {duration} minutes')
	elif ctx.invoked_subcommand is None and name is None:
		typer.echo(ctx.get_help())


@block_app.command('stop', help='Stop the current block (requires passphrase)')
def stop():
	pass
