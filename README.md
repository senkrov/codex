# Codex

Codex is a desktop media browser application for Arch Linux, featuring a dynamic, 3D-style interface for navigating TV show seasons and episodes.

## Features

*   Scans a local directory for movie and show files.
*   Fetches media information and artwork from The Movie Database (TMDb).
*   Displays movies and shows in a simple grid.
*   Presents seasons and episodes in a dynamic, horizontally scrolling "deck of cards" with 3D perspective effects.
*   Fully navigable via keyboard shortcuts.

## Setup

1.  Install Python 3.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment: `source venv/bin/activate`
4.  Install the dependencies: `pip install -r requirements.txt`
5.  Run the application: `python main.py`

## Usage

*   **Arrow Keys (J, K, U, D):** Navigate through media grids.
*   **L / Enter / Space:** Select an item.
*   **H:** Go back to the previous view.
*   **O:** Open the settings view.