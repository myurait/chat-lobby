# Ideal Experience Spec Template

Use this template to normalize the active ideal experience document after requirement discovery.

## Output Rule

- The canonical output path is `design/00-ideal-experience.md`.
- Do not create a second active ideal experience document with another filename.
- If this document is derived from interviews, imported specifications, or superseded drafts, archive those source materials under `reference/historical-documents/`.
- Add or update the corresponding entry in `reference/historical-documents/INDEX.md`.

## 1. Purpose

- Why this document exists
- What planning decisions it should drive

## 2. Product Definition

- One-sentence definition
- Product boundary

## 3. User and Context

- Primary user
- Working environment
- Device continuity expectations

## 4. Core Problems

- Main frustrations
- What gets fragmented or repeated
- Why current workflow fails

## 5. Ideal Experience Summary

- What the user should be able to do naturally
- What should feel automatic
- What should stop being manual

## 6. Experience Pillars

- Pillar:
  - Why it matters
  - What is in scope
  - What failure looks like

## 7. Representative Scenarios

- Scenario:
  - Trigger
  - Expected behavior
  - Correction behavior if the system guesses wrong

## 8. Acceptance Signals

- What user-visible evidence indicates the experience is working
- What would show the implementation is missing the intent

## 9. Non-Goals

- Explicitly out of scope items

## 10. Planning Implications

- Candidate epics
- Open design questions
- Validation constraints
