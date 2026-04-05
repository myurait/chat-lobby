# Workspace

This directory is mounted into the `open-terminal` container at `/workspace`.

## Layout

- `repos/`: runtime clones and scratch repositories used from Open Terminal or File Browser
- `templates/chatlobby-canonical/`: fixed initial structure for the shared canonical Git repository

## Usage

1. Open Terminal from Open WebUI.
2. Work under `/workspace/repos` for temporary clones or experiments.
3. Copy `templates/chatlobby-canonical/` when starting a new shared canonical repository.

Runtime clones under `repos/` are intentionally ignored from the root repository.
