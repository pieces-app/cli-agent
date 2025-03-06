## Testing a remote branch locally

1. Clone this repo locally `git clone <repo>`
2. Fetch remote branches `git fetch`
3. Checkout the feature branch `git checkout <feat-branch-name>`
4. Install dependencies `poetry install`
5. Run the CLI with `python src/pieces <CLI command> ` (or `python3`)

Ex: `python src/pieces help` or `python src/pieces config --editor vim`

## Testing a staging release

1. Download and unzip the release for your architecture
2. `pip install path/to/download` (or `pip3`)
3. `python -m pieces version` (or `python3`) <-- check you are running the staging version

Ex: `python -m pieces help` or `python -m pieces config --editor vim`

## Release

```
git tag <tagname>
git push origin <tagname>
```
