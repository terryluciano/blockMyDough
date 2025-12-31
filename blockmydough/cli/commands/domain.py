import typer
from typing import Annotated

domain_app = typer.Typer()


@domain_app.command('add')
def add(domain: Annotated[str, typer.Argument()]):
	pass


@domain_app.command('remove')
def remove(domain: Annotated[str, typer.Argument()]):
	pass


@domain_app.command('list')
def list():
	pass
