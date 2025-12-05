from .database import database_bp
from .health import health_bp
from .auth.login import login_bp
from .auth.register import register_bp
from .auth.a2f  import active_a2f, check_a2f, diable_a2f, login_a2f, statue_a2f_route
from .docs import docs_bp
from .user import name_user, statue_session, change_password


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
    app.register_blueprint(statue_a2f_route, url_prefix=api_prefix)
    app.register_blueprint(statue_session, url_prefix=api_prefix)
    app.register_blueprint(change_password, url_prefix=api_prefix)
    app.register_blueprint(docs_bp)
