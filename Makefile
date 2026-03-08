N ?=

run:
	uv run expences.py $(if $(N),-n $(N))
