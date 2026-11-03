REPO := noi/certbot-dns-lightsail

# Build and push the Docker image on GitHub Actions.
# Optional: VERSION, CERTBOT_VERSION, LATEST (true/false)
#   make docker
#   make docker VERSION=0.2.0 CERTBOT_VERSION=5.1.0 LATEST=false
.PHONY: docker
docker:
	gh workflow run docker.yml --repo $(REPO) \
		$(if $(VERSION),-f version=$(VERSION)) \
		$(if $(CERTBOT_VERSION),-f certbot-version=$(CERTBOT_VERSION)) \
		$(if $(LATEST),-f latest=$(LATEST))
	@echo 'Run "make docker-watch" to follow it.'

.PHONY: docker-watch
docker-watch:
	gh run watch --repo $(REPO) \
		$$(gh run list --repo $(REPO) --workflow docker.yml --limit 1 --json databaseId --jq '.[0].databaseId')
