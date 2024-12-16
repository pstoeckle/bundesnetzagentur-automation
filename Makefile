quick-format:
	uv run -- ruff format
	uv run -- ruff check --fix
format:
	uv run -- black .
	uv run -- isort --profile black .

report-sms:
	uv run -- python \
	bundesnetzagentur_automation/__init__.py \
	configuration.json \
	"+491733171381" \
	t.txt \
	12.12.2024

install-chromedriver:
	curl \
		--location \
		--fail \
		--show-error \
		--silent \
		--remote-name \
		https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.108/mac-x64/chromedriver-mac-x64.zip
	unzip chromedriver-mac-x64.zip
	chmod +x chromedriver-mac-x64/chromedriver
	mv chromedriver-mac-x64/chromedriver /usr/local/bin/chromedriver
	rm -rf chromedriver-mac-x64
	rm chromedriver-mac-x64.zip
