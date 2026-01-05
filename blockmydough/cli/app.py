import random

import typer
from rich.panel import Panel

from blockmydough.cli.commands.block import block_app
from blockmydough.cli.commands.domain import domain_app
from blockmydough.cli.commands.preset import preset_app
from blockmydough.cli.commands.schedule import schedule_app
from blockmydough.cli.commands.passphrase import passphrase_app
from blockmydough.cli.commands.daemon import daemon_app
from blockmydough.cli.ui import app_console
from blockmydough.constants import DUMB_MESSAGES
from blockmydough.core import state

app = typer.Typer(help='BlockMyDough - A self-control tool to block distracting websites.')

# Sub Commands
app.add_typer(schedule_app, name='schedule')
app.add_typer(preset_app, name='preset')
app.add_typer(domain_app, name='domain')
app.add_typer(block_app, name='block')
app.add_typer(passphrase_app, name='passphrase')
app.add_typer(daemon_app, name='daemon')


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
	if ctx.invoked_subcommand is None:
		random_message = DUMB_MESSAGES[random.randint(0, len(DUMB_MESSAGES) - 1)]

		app_console.print(
			Panel(
				f'[bold]Welcome to BlockMyDough[/bold]\n[italic]{random_message}[/italic]',
				title='Welcome',
				padding=(1, 2),
			),
			style='rgb(175,15,224)',
			justify='center',
			no_wrap=False,
		)

		app_console.print(state.read_state())


@app.command()
def status():
	"""Show current blocking status."""
	app_console.status('Status is not implemented yet...')


if __name__ == '__main__':
	app()
