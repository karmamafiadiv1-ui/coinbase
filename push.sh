#!/bin/bash
git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/karmamafiadiv1-ui/coinbase.git"
git push origin main
