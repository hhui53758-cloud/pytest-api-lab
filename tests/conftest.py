"""自动启动服务、隔离数据库、登录与测试数据清理。"""
import logging
import socket
import threading
import time

import pytest
import uvicorn

from app.api import create_app
from framework.client import ApiClient
from framework.config import ROOT, load_settings
from framework.database import DatabaseProbe


@pytest.fixture(scope="session")
def settings():
    return load_settings()


@pytest.fixture(scope="session", autouse=True)
def file_logging():
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    handler = logging.FileHandler(log_dir / "api-tests.log", mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger = logging.getLogger("api_tests")
    previous_level = logger.level
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    yield
    logger.removeHandler(handler)
    logger.setLevel(previous_level)
    handler.close()


@pytest.fixture(scope="session")
def test_environment(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("task-api") / "test.sqlite3"
    application = create_app(db_path)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    listener.listen()
    server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=port,
        log_level="warning", access_log=False, loop="asyncio", lifespan="on"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started:
            if not thread.is_alive() or time.monotonic() >= deadline:
                pytest.fail("The isolated API did not start within 10 seconds")
            time.sleep(0.05)
        yield {"base_url": f"http://127.0.0.1:{port}", "db_path": db_path}
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()
        if thread.is_alive():
            raise RuntimeError("The isolated API did not shut down")


@pytest.fixture
def api_client(test_environment, settings):
    client = ApiClient(test_environment["base_url"], settings["timeout"])
    yield client
    client.close()


@pytest.fixture(scope="session")
def auth_tokens(test_environment, settings):
    client = ApiClient(test_environment["base_url"], settings["timeout"])
    tokens = {}
    try:
        for name, account in settings["accounts"].items():
            response = client.post("/auth/login", json=account)
            assert response.status_code == 200, "Demo account login failed"
            tokens[name] = response.json()["access_token"]
        return tokens
    finally:
        client.close()


@pytest.fixture
def api_alice(api_client, auth_tokens):
    api_client.set_token(auth_tokens["alice"])
    return api_client


@pytest.fixture
def api_bob(test_environment, settings, auth_tokens):
    client = ApiClient(test_environment["base_url"], settings["timeout"])
    client.set_token(auth_tokens["bob"])
    yield client
    client.close()


@pytest.fixture
def db_probe(test_environment):
    return DatabaseProbe(test_environment["db_path"])


@pytest.fixture
def task_factory(api_alice):
    task_ids = []

    def create(**payload):
        response = api_alice.post("/tasks", json=payload)
        if response.status_code == 201:
            task_ids.append(response.json()["id"])
        return response

    yield create
    for task_id in reversed(task_ids):
        response = api_alice.delete(f"/tasks/{task_id}")
        assert response.status_code in (204, 404), "Test task cleanup failed"


@pytest.fixture(autouse=True)
def case_logging(request, file_logging):
    logger = logging.getLogger("api_tests")
    logger.info("CASE_START %s", request.node.nodeid)
    yield
    logger.info("CASE_END %s", request.node.nodeid)
