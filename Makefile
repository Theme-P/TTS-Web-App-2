# Makefile for TTS Web App

IMAGE_NAME = tts-webapp
DOCKER_ID = n301ix

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

# Docker Hub operations
tag:
	docker tag $(IMAGE_NAME) $(DOCKER_ID)/$(IMAGE_NAME):latest

push:
	docker push $(DOCKER_ID)/$(IMAGE_NAME):latest

full-release: build tag push
