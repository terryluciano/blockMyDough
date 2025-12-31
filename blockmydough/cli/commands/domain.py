from typing import Annotated

import typer

domain_app = typer.Typer(help='Manage domains for permanent blocking')


@domain_app.command('add', help='Add a domain to the block list')
def add(domain: Annotated[str, typer.Argument(help='Domain to add')]):
	pass


@domain_app.command('remove', help='Remove a domain from the block list')
def remove(domain: Annotated[str, typer.Argument(help='Domain to remove')]):
	pass


@domain_app.command('list', help='List all domains in the block list')
def list():
	pass
