N ?=

run:
	uv run python tui.py $(if $(N),-n $(N))

cli:
	uv run python expences.py $(if $(N),-n $(N))
