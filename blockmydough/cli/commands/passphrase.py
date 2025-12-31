import typer

passphrase_app = typer.Typer()


@passphrase_app.command('set', help='Set the passphrase for the app')
def set():
	pass


@passphrase_app.command('verify', help='Verify the passphrase for the app')
def remove():
	pass
