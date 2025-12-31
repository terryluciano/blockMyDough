from typing import Annotated

import typer
from rich.panel import Panel

from blockmydough.cli.ui import app_console
from blockmydough.core.presets import PRESETS

preset_app = typer.Typer(help='Manage presets')


@preset_app.command('list', help='Displays a list of all the custom and pre-defined presets')
def preset_list():
	for key, value in PRESETS.items():
		clean_value = [x for x in value if not x.startswith('www.')]

		preset_list: str = ''

		for index, val in enumerate(clean_value):
			if not val.startswith('www.'):
				preset_list += f'{val}{"" if index == len(clean_value) - 1 else "\n"}'

		if key != 'all':
			app_console.print(
				Panel(
					f'{preset_list}',
					title=key.capitalize(),
					style='rgb(175,15,224)',
					padding=(0),
					expand=True,
				)
			)


@preset_app.command('create', help='Create a new custom preset')
def create(
	name: Annotated[str, typer.Argument(help='Set preset name')],
	domain: Annotated[
		str,
		typer.Option('--domain', '-d', help='List of domains'),
	] = '',
):
	pass


@preset_app.command('remove', help='Remove selected preset')
def remove(
	name: Annotated[str, typer.Argument(help="Name or id of preset you'd like to remove")],
):
	pass


@preset_app.command('add', help='Add domain(s) to selected preset')
def add(
	preset: Annotated[str, typer.Option('--preset', '-p', help='Preset name or id')],
	domain: Annotated[
		str,
		typer.Option('--domain', '-d', help='Comma-separated domains to add to selected preset'),
	],
):
	app_console.print(preset)

	clean_domains = domain.split(',')

	app_console.print(clean_domains)
