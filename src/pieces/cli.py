import typer
import commands as commands
app = typer.Typer()


@app.command()
def ask(query: str):
    commands.ask(query)

@app.command()
def search(query: str):
    commands.search(query)

@app.command()
def list():
    commands.list_assets()

@app.command()
def open():
    commands.open_asset()

@app.command()
def save():
    commands.save_asset()

@app.command()
def edit():
    commands.edit_asset()

@app.command()
def delete():
    commands.delete_asset()

@app.command()
def create():
    commands.create_asset()

@app.command()
def check():
    commands.check()

if __name__ == "__main__":
    app()