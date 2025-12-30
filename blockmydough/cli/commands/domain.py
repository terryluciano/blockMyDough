import typer

domain_app = typer.Typer()


@domain_app.command('add')
def add(domain: str):
	pass


@domain_app.command('remove')
def remove(domain: str):
	pass


@domain_app.command('list')
def list():
	pass
