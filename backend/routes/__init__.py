from .database import database_bp
from .health import health_bp
from .login import login_bp, name_user
from .register import register_bp
from .a2f  import active_a2f, check_a2f, diable_a2f, login_a2f
from .docs import docs_bp


def register_blueprints(app):
    api_prefix = "/api"
    app.register_blueprint(health_bp, url_prefix=api_prefix)
    app.register_blueprint(database_bp, url_prefix=api_prefix)
    app.register_blueprint(login_bp, url_prefix=api_prefix)
    app.register_blueprint(register_bp, url_prefix=api_prefix)
    app.register_blueprint(active_a2f, url_prefix=api_prefix)
    app.register_blueprint(check_a2f, url_prefix=api_prefix)
    app.register_blueprint(diable_a2f, url_prefix=api_prefix)
    app.register_blueprint(login_a2f, url_prefix=api_prefix)
    app.register_blueprint(name_user, url_prefix=api_prefix)
    app.register_blueprint(docs_bp)
