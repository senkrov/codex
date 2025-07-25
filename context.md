# codex - context.md

This file serves as a living document for the codex project, providing essential context and historical information for both human developers and AI agents (like Gemini). Its purpose is to ensure efficient and accurate development by preserving key decisions, changes, and future plans.

## Project Overview

**Application Type:** Desktop media browser application for Arch linux.

**Core Functionality:**
*   Scans a specific local directory for movie and show files.
*   Generates thumbnails for media files.
*   Organizes scanned media into a browsable catalog (movies and shows displayed as modern graphical cards with full-card artwork relating to the media and basic information such as name and release dates sitting inside the card in a semi-transparent area overlapping a small portion at the bottom of the card, seasons displayed as smaller cards with season names, episodes displayed as rowed lists)
*   Displays media using a graphical user interface.
*   Allows navigation and selection of media items via keyboard shortcuts.

## Architecture and Design Choices

**Technology Stack:**
*   **Language:** Python 3
*   **GUI Framework:** PyQt6
*   **Metadata:** The Movie Database (TMDb) API
*   **Image Handling:** `requests` for downloading, with local caching.

**Key Components:**
*   **`main.py`:** The application's entry point, responsible for the main window, UI layout, and event handling.
*   **`scanner.py`:** Handles scanning the media directory for movies and shows.
*   **`tmdb.py`:** A wrapper for the TMDb API, used to fetch media metadata.
*   **`config.py`:** Manages saving and loading the media directory path.
*   **`cache.py`:** Implements a local file cache for downloaded images to improve performance.
*   **`worker.py`:** Uses `QThreadPool` and `QRunnable` to perform network operations (image and metadata downloading) in the background, preventing the UI from freezing.
*   **`ui/`:** A directory containing custom UI components, such as `MediaCard`, `ShowCard`, and `SeasonCard`.

### Key Design Principles

*   **Full Keyboard Navigability:** The application's user interface will be designed to be entirely navigable via keyboard shortcuts, eliminating the need for mouse interaction for core functionalities.
*   **Specific Directory Scanning:** The media scanner will operate exclusively on a single, user-defined root directory. It is assumed that media files within this directory will adhere to a specific, pre-defined organizational structure. A pop-up at app initialization will request the exact path to the media folder expected to house directories such as "movies", "shows", etc...).
*   **Asynchronous Operations:** All network requests are handled in the background to ensure a responsive and non-blocking user interface.
*   **Local Caching:** All downloaded images are cached locally to minimize network requests and improve loading times.

## Session Summaries and Changes

**Session 1 (2025-07-24):**
*   **Project Setup:** Initialized the project with a basic PyQt6 application structure, including a `.gitignore`, `requirements.txt`, and `README.md`.
*   **Media Scanner:** Implemented the initial media scanner to identify movies and shows based on a predefined directory structure.
*   **TMDb Integration:** Integrated the TMDb API to fetch movie and show metadata, including posters. After significant debugging of the API key and request methods, the connection was successfully established.
*   **UI Development:** Created a card-based UI to display media, with custom widgets for movies, shows, and seasons. Implemented a tabbed interface to separate movies and shows, and a stacked widget to navigate between shows, seasons, and episodes.
*   **Keyboard Navigation:** Implemented keyboard navigation to move between media cards using the arrow keys.
*   **Configuration:** Added a configuration system to save and load the media directory path, so the user only needs to select it on the first launch.
*   **Performance Optimization:** Implemented a background worker system to handle image and metadata downloads asynchronously, preventing the UI from freezing. Added a local caching system for images to reduce network requests and improve performance.
*   **UI Refinements:** Moved the "Change Media Directory" button to a less prominent folder icon on the tab bar and implemented a fixed window size to prevent resizing.
*   **Bug Fixing:** Addressed several bugs, including a `KeyError` when handling TMDb API responses, a typo that caused a crash, and incorrect season sorting.

## Reasoning for Refactorings/Feature Additions

*(To be documented as changes are made)*

## Known Issues and Future Plans

*(To be maintained throughout the project lifecycle)*

---

**Note to Developers and AI Agents:**
This `context.md` file is critical for maintaining context and efficiency. Please ensure it is kept up-to-date whenever significant changes, design decisions, or new issues arise. Outdated information can lead to inefficiencies and errors.

also note:

* Maintain Context for AI Agents:** Comments serve as crucial "breadcrumbs" for AI agents, allowing them to quickly grasp the intent and context of code, significantly improving their ability to assist effectively across sessions. This reduces the need for repetitive explanations and re-analysis.
* Context Preservation: Code comments are vital for preserving the rationale behind
complex logic or non-obvious design choices, enabling AI agents (like me) to
maintain accurate context across development sessions.
* Efficiency & Accuracy: Clear, concise comments reduce the need for extensive
code re-analysis, leading to more efficient and accurate modifications by both
human developers and AI.
* Keep Comments Up-to-Date:** Outdated comments are worse than no comments. Ensure comments are revised whenever the corresponding code changes.
