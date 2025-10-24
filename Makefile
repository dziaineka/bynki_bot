NAME   := skaborik/bynki_bot
TAG    := $$(git describe --tags --abbrev=0)
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest

build:
	@docker buildx build --platform linux/amd64,linux/arm64 -t ${IMG} .
	@docker buildx build --platform linux/amd64,linux/arm64 -t ${LATEST} .

push:
	@docker buildx build --platform linux/amd64,linux/arm64 -t ${IMG} --push .
	@docker buildx build --platform linux/amd64,linux/arm64 -t ${LATEST} --push .

pyenv:
	@python3 -m venv .venv
	@. .venv/bin/activate && uv pip install -e .
