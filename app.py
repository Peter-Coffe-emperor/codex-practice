from datetime import datetime, timezone
from importlib.util import find_spec
from typing import Any, Callable

RouteHandler = Callable[[], dict[str, str]]
RouteDecorator = Callable[[RouteHandler], RouteHandler]

if find_spec("flask") is not None:
    from flask import Flask
else:
    class _Response:
        def __init__(self, data: dict[str, str], status_code: int = 200) -> None:
            self._data = data
            self.status_code = status_code

        def get_json(self) -> dict[str, str]:
            return self._data

    class _TestClient:
        def __init__(self, routes: dict[tuple[str, str], RouteHandler]) -> None:
            self._routes = routes

        def get(self, path: str) -> _Response:
            handler = self._routes.get(("GET", path))
            if handler is None:
                return _Response({"error": "not found"}, 404)
            return _Response(handler())

    class Flask:
        def __init__(self, name: str) -> None:
            self.name = name
            self._routes: dict[tuple[str, str], RouteHandler] = {}

        def route(
            self,
            path: str,
            methods: list[str] | None = None,
        ) -> RouteDecorator:
            route_methods = methods or ["GET"]

            def decorator(func: RouteHandler) -> RouteHandler:
                for method in route_methods:
                    self._routes[(method.upper(), path)] = func
                return func

            return decorator

        def get(self, path: str) -> RouteDecorator:
            return self.route(path, methods=["GET"])

        def test_client(self) -> _TestClient:
            return _TestClient(self._routes)

        def run(self, **kwargs: Any) -> None:
            raise RuntimeError("Flask is not installed in this environment.")


app = Flask(__name__)


@app.route("/")
def index() -> dict[str, str]:
    return {"message": "Welcome to Codex Practice!"}


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    app.run(debug=True)
