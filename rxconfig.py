import reflex as rx

config = rx.Config(
    app_name="Trust_Web",
    db_url="sqlite:///db/reflex.db",
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
)
