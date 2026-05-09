# Prompt Engineering Changelog

All notable changes to the `prompt.txt` logic will be documented in this file.

## [3.1.0] - 2025-12-30
### Fixed
- Validated output format against regression cases using GPT-4o.
- Confirmed handling of "mixed-language" inputs (Chinese/English tags).

## [3.0.0] - 2025-12-30
### Added
- **Time Handling**: Explicit instruction to preserve "HH:mm " format if input starts with time.
- **Golden Dataset**: Established `cases.yaml` as the source of truth for regression testing.

### Changed
- **Summarization**: Refined rules to keep "narrative feel" while removing fillers ("傻瓜傻瓜", "来来来").
- **Tagging**: Enforced 2-4 English hashtags as the primary format.

### Removed
- Removed legacy "Auto-Translation" instructions (focused on raw meaning).

## [2.0.0] - 2025-12-25
### Changed
- Major refactor from "Chat Style" to "Log Style".
- Introduced structured 5-category system (🛠️, 🧠, 🥗, 📅, 📝).

## [1.0.0] - 2025-12-01
### Added
- Initial experimental prompt for Siri-to-Note workflow.
