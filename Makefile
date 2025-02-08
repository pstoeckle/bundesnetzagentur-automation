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

CHROME_VERSION :=$(shell curl \
	--connect-timeout 5 \
	--fail \
	--location \
	--max-time 120 \
	--proto '=https' \
	--show-error \
	--silent \
	--tlsv1.2 \
	https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json  \
	| jq --raw-output '.["channels"]["Stable"]["version"]')

install-chromedriver:
	curl \
		--connect-timeout 5 \
		--fail \
		--location \
		--max-time 120 \
		--proto '=https' \
		--remote-name \
		--show-error \
		--silent \
		--tlsv1.2 \
		https://storage.googleapis.com/chrome-for-testing-public/$(CHROME_VERSION)/mac-x64/chromedriver-mac-x64.zip
	unzip chromedriver-mac-x64.zip
	chmod +x chromedriver-mac-x64/chromedriver
	mv chromedriver-mac-x64/chromedriver /usr/local/bin/chromedriver
	rm -rf chromedriver-mac-x64
	rm chromedriver-mac-x64.zip
