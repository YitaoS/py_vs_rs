PYTHON_FILES := src tests

.PHONY: install format lint run report

install:
	pip install --upgrade pip
	pip install .[dev]

format:
	black $(PYTHON_FILES)

lint:
	flake8 $(PYTHON_FILES) --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 $(PYTHON_FILES) --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

run:
	python3 src/main.py

deploy:
	git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
	git config --local user.name "github-actions[bot]"
	git add ./*.md
	git add ./*.png
	git commit -m "Add report and images"

test:
	PYTHONPATH=src pytest -s tests/test_example.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.png" -delete
	rm -f *report.md
	rm -f descr*

check-format:
	black --check $(PYTHON_FILES)

ci: lint test check-format
