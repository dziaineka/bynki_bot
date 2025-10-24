FROM python:3.14.0-slim-trixie

WORKDIR /usr/src/app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --no-cache .

COPY . .

CMD [ "python", "./main.py" ]
