from datetime import datetime, timezone
from importlib.util import find_spec
from typing import Any, Callable

from models import create_todo, delete_todo, get_all_todos, get_todo, update_todo

RouteReturn = dict[str, Any] | list[dict[str, Any]] | tuple[dict[str, Any], int]
RouteHandler = Callable[..., RouteReturn]
RouteDecorator = Callable[[RouteHandler], RouteHandler]

if find_spec("flask") is not None:
    from flask import Flask, jsonify, request
else:
    class _Request:
        _json: dict[str, Any] | None = None

        def get_json(self, silent: bool = False) -> dict[str, Any] | None:
            return self._json

    request = _Request()

    class _Response:
        def __init__(self, data: Any, status_code: int = 200) -> None:
            self._data = data
            self.status_code = status_code

        def get_json(self) -> Any:
            return self._data

    def jsonify(data: Any) -> _Response:
        return _Response(data)

    class _TestClient:
        def __init__(self, routes: dict[tuple[str, str], RouteHandler]) -> None:
            self._routes = routes

        def _request(
            self,
            method: str,
            path: str,
            json: dict[str, Any] | None = None,
        ) -> _Response:
            request._json = json
            handler, args = self._match_route(method, path)
            if handler is None:
                return _Response({"error": "not found"}, 404)

            result = handler(*args)
            if isinstance(result, tuple):
                data, status_code = result
                response = data if isinstance(data, _Response) else _Response(data)
                response.status_code = status_code
                return response
            if isinstance(result, _Response):
                return result
            return _Response(result)

        def _match_route(
            self,
            method: str,
            path: str,
        ) -> tuple[RouteHandler | None, list[int]]:
            direct = self._routes.get((method, path))
            if direct is not None:
                return direct, []

            for (route_method, route_path), handler in self._routes.items():
                if route_method != method:
                    continue
                prefix = route_path.split("<int:todo_id>")[0]
                if "<int:todo_id>" not in route_path or not path.startswith(prefix):
                    continue
                raw_id = path.removeprefix(prefix)
                if raw_id.isdigit():
                    return handler, [int(raw_id)]
            return None, []

        def get(self, path: str) -> _Response:
            return self._request("GET", path)

        def post(self, path: str, json: dict[str, Any] | None = None) -> _Response:
            return self._request("POST", path, json)

        def put(self, path: str, json: dict[str, Any] | None = None) -> _Response:
            return self._request("PUT", path, json)

        def delete(self, path: str) -> _Response:
            return self._request("DELETE", path)

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

        def post(self, path: str) -> RouteDecorator:
            return self.route(path, methods=["POST"])

        def put(self, path: str) -> RouteDecorator:
            return self.route(path, methods=["PUT"])

        def delete(self, path: str) -> RouteDecorator:
            return self.route(path, methods=["DELETE"])

        def test_client(self) -> _TestClient:
            return _TestClient(self._routes)

        def run(self, **kwargs: Any) -> None:
            raise RuntimeError("Flask is not installed in this environment.")


app = Flask(__name__)


def _is_invalid_title(title: Any) -> bool:
    return not isinstance(title, str) or title.strip() == ""


def _get_done(data: dict[str, Any]) -> bool:
    return bool(data.get("done", False))


def _not_found() -> tuple[Any, int]:
    return jsonify({"error": "Not found"}), 404


@app.route("/")
def index() -> Any:
    return jsonify({"message": "Welcome to Codex Practice!"})


@app.get("/health")
def health() -> Any:
    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.post("/api/todos")
def create_todo_endpoint() -> tuple[Any, int]:
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if _is_invalid_title(title):
        return jsonify({"error": "Title is required"}), 400

    todo = create_todo(title.strip(), _get_done(data))
    return jsonify(todo), 201


@app.get("/api/todos")
def list_todos_endpoint() -> Any:
    return jsonify(get_all_todos())


@app.get("/api/todos/<int:todo_id>")
def get_todo_endpoint(todo_id: int) -> Any:
    todo = get_todo(todo_id)
    if todo is None:
        return _not_found()

    return jsonify(todo)


@app.put("/api/todos/<int:todo_id>")
def update_todo_endpoint(todo_id: int) -> Any:
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if _is_invalid_title(title):
        return jsonify({"error": "Title is required"}), 400

    todo = update_todo(todo_id, title.strip(), _get_done(data))
    if todo is None:
        return _not_found()

    return jsonify(todo)


@app.delete("/api/todos/<int:todo_id>")
def delete_todo_endpoint(todo_id: int) -> Any:
    if not delete_todo(todo_id):
        return _not_found()

    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(debug=True)
