REPO := noi/certbot-dns-lightsail

# Build and push the Docker image on GitHub Actions, and follow the run.
# Optional: VERSION, CERTBOT_VERSION, LATEST (true/false)
#   make docker
#   make docker VERSION=0.2.0 CERTBOT_VERSION=5.1.0 LATEST=false
.PHONY: docker
docker:
	@out="$$(gh workflow run docker.yml --repo $(REPO) \
		$(if $(VERSION),-f version=$(VERSION)) \
		$(if $(CERTBOT_VERSION),-f certbot-version=$(CERTBOT_VERSION)) \
		$(if $(LATEST),-f latest=$(LATEST)) 2>&1)" || { echo "$$out" >&2; exit 1; }; \
	echo "$$out"; \
	id="$$(echo "$$out" | grep -o 'actions/runs/[0-9]*' | head -n 1 | cut -d / -f 3)"; \
	if [ -z "$$id" ]; then echo 'Run ID not found; check https://github.com/$(REPO)/actions' >&2; exit 1; fi; \
	gh run watch "$$id" --repo $(REPO) --exit-status
