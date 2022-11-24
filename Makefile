lint:
	docker run -u 1000:1000 \
		--rm \
		-e LINT_FOLDER_PYTHON=. \
		-v $(CURDIR):/app divio/lint /bin/lint --run=python
