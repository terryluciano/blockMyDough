import typer
from rich.panel import Panel
from blockmydough.cli.ui import app_console
from blockmydough.core.presets import PRESETS


preset_app = typer.Typer()


@preset_app.command('list')
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
