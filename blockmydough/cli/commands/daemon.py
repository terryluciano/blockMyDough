import typer

daemon_app = typer.Typer()


@daemon_app.command(help='Start the blockmydough daemon')
def start():
	print('start')


@daemon_app.command(help='Stop the blockmydough daemon')
def stop():
	print('stop')
