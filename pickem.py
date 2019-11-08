from app import app, db
from app.models import User, Week, Game


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Game': Game, 'Week':Week}