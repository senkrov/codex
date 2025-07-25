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

### Key Design Principles

*   **Full Keyboard Navigability:** The application's user interface will be designed to be entirely navigable via keyboard shortcuts, eliminating the need for mouse interaction for core functionalities.
*   **Specific Directory Scanning:** The media scanner will operate exclusively on a single, user-defined root directory. It is assumed that media files within this directory will adhere to a specific, pre-defined organizational structure. A pop-up at app initialization will request the exact path to the media folder expected to house directories such as "movies", "shows", etc...).

*(To be filled as the project progresses)*

## Session Summaries and Changes

*(To be updated after each significant development session)*

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
