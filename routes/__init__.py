from flask import Blueprint

def register_routes(app):
    from .auth_routes import auth_bp
    from .task_routes import task_bp
    from .admin_routes import admin_bp
    # from .misc_routes import misc_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(admin_bp)
    # app.register_blueprint(misc_bp)