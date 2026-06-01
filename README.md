# tretter

Join multiple weather observation data sources into one.

## usage
```bash
$ uv sync
$ uv run src/ingest.py
```

### add new dependencies
```bash
$ uv add <pip package name>
```

## testing
```bash
$ uv run pytest
```

## linting
```bash
$ ty check
```

## todo
- consider using polars/arrow? to manage sample data
- pytest to unit test stuff
- consider using pydantic to manage env/options
