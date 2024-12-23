FROM python:3.12-slim

WORKDIR /docs

COPY pyproject.toml .
COPY poetry.lock .

RUN apt-get update && apt-get install -y git && \
    pip install --no-cache-dir poetry && \
    poetry install --no-root --only docs

COPY mkdocs.yml .
COPY docs/ docs/
COPY docs-resources/ docs-resources/

COPY .git .git

RUN poetry run mkdocs build

FROM nginx:alpine

COPY --from=0 /docs/site /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 