TORTOISE_ORM = {
    "connections": {
        "default": "postgres://saleor:saleor@localhost:5532/stavi"
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
