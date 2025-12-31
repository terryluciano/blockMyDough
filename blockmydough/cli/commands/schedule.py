from typing import Annotated

import typer

schedule_app = typer.Typer(help='Manage schedules for presets')


@schedule_app.command('add', help='Add a new schedule for a preset')
def add(
	preset: Annotated[
		str, typer.Argument(help="Target preset name or id you'd like to put on a schedule")
	],
	name: Annotated[str, typer.Option('--name', '-n', help='Name of the schedule')],
	days: Annotated[
		str,
		typer.Option(
			'--days',
			'-dy',
			help='Comma-separated days for the schedule (e.g. `mon,tue,thur` or `fri`)',
		),
	],
	from_time: Annotated[
		str,
		typer.Option('--from', '-f', help='Start time of the schedule HH:MM (e.g. 09:00 or 17:00)'),
	],
	to_time: Annotated[
		str,
		typer.Option('--to', '-t', help='End time of the schedule HH:MM (e.g. 12:00 or 20:00)'),
	],
):
	pass


@schedule_app.command('list', help='Display a list of the active schedules')
def list():
	pass


@schedule_app.command('remove', help='Remove a selected schedule')
def remove(name: Annotated[str, typer.Argument(help='Selected name or id of preset')]):
	pass


@schedule_app.command('status', help='Display the status of the active schedules')
def status():
	pass
