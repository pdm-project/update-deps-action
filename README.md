# PDM update dependencies GitHub Action

## Usage

Example workflow:

```yaml
name: Update dependencies

on:
  schedule:
    - cron: "0 0 * * *"

jobs:
  update-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Update dependencies
        uses: pdm-project/update-deps-action@main
```

## Inputs

```yaml
with:
  # The personal access token, default: ${{ github.token }}
  token: ${{ secrets.GH_TOKEN }}
  # The commit message"
  commit-message: "chore: Update pdm.lock"
  # The PR title
  pr-title: "Update dependencies"
  # The update strategy, can be 'reuse', 'eager' or 'all'
  update-strategy: eager
  # Whether to install PDM plugins before update
  install-plugins: "false"
  # Whether commit message contains signed-off-by
  sign-off-commit: "false"
```
