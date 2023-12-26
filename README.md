[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://https://docker.com/)
[![CI](https://github.com/agn-7/ai3d-backend/workflows/build/badge.svg)](https://github.com/agn-7/ai3d-backend/actions/workflows/github-actions.yml)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![codecov](https://codecov.io/gh/agn-7/ai3d-backend/graph/badge.svg?token=RGwuSevG8u)](https://codecov.io/gh/agn-7/ai3d-backend)

# Ai3D Backend
Async smart 3D model creator and editor backend powered by GPT on top of FastAPI

## Setup
It contains two generic entity models Interaction and Message.
We store all of the data in the Postgres database.
The interaction with the database is done with the [SQLAlchemy](https://www.sqlalchemy.org/) library, and the simple GET and POST endpoints are exposed via the API, which is written with the [FastAPI](https://fastapi.tiangolo.com/) framework.

To manage dependencies, we use [poetry](https://python-poetry.org/).

To launch an API instance, you should:
1. Have a running Postgres instance, e.g. in a container. The application will read the [.env](/.env) file to access the database.
2. Create a virtual environment and install the dependencies in it. You can run `poetry install` for that.
3. Use [start_app.sh](/start_app.sh) to run the server. By default, it will bind to http://localhost:8000.
4. An automatically generated documentation can be found at http://localhost:8000/docs. The endpoints are accessible at http://localhost:8000/api/<endpoint_name>.

You can also run the project via `docker-compose` (i.e. `docker compose up -d`) on port `80` in which you would need the [.docker.env](/.docker.env) containing the following variable to create the database:

```
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://<username>:<password>@ai3d_db/<db-name>
```

