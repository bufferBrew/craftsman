# existing-python-fixture

## Development

Run the check suite with:

```
poetry run tox -e lint,test
```

Do not use plain `pytest` — this project runs lint and tests together through `tox`.
