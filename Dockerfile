# Datasette image for til.abd.dev, deployed on Coolify (cfy1).
# tils.db and shots/ are built by .github/workflows/build.yml before
# `docker build`.
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "datasette>=0.65.1,<1.0" \
    datasette-template-sql \
    "datasette-sitemap>=1.0" \
    "datasette-atom>=0.7" \
    datasette-json-html \
    beautifulsoup4 \
    "datasette-debug-asgi>=1.1" \
    "datasette-graphql>=2.2" \
    datasette-block-robots \
    datasette-llm-embed

COPY metadata.yaml tils.db ./
COPY plugins ./plugins
COPY templates ./templates
COPY static ./static
COPY shots ./shots

EXPOSE 8001

CMD ["datasette", "serve", "-i", "tils.db", \
     "--host", "0.0.0.0", "--port", "8001", \
     "--metadata", "metadata.yaml", \
     "--plugins-dir", "plugins", \
     "--template-dir", "templates", \
     "--static", "static:static", \
     "--static", "shots:shots", \
     "--setting", "force_https_urls", "on"]
