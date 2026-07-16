# GLaDOS Daily Check-in

This repository runs a GitHub Actions workflow to check in to GLaDOS every day.

## GitHub Actions setup

The workflow file is `.github/workflows/runGladosAction.yml`.

It runs at 01:30 UTC every day, which is 09:30 in Asia/Shanghai, and can also be run manually from the GitHub Actions tab.

## Required secret

Add this repository secret:

- `GLADOS_COOKIE`: your GLaDOS browser cookie.

For multiple accounts, join cookies with `&`.

Do not paste the cookie into the workflow file, README, commit messages, issues, or logs.

## Optional secret

- `PUSHPLUS_TOKEN`: PushPlus token for check-in result notifications.

## Local test

```bash
python -m unittest
```
