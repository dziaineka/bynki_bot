NAME   := skaborik/bynki_bot
TAG    := $$(git describe --tags --abbrev=0)
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest

build:
	@docker build -t ${IMG} .
	@docker build -t ${LATEST} .

push:
	@docker push ${IMG}
	@docker push ${LATEST}
