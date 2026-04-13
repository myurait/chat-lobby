# Requirement Discovery Rules

## Purpose

Define how ChatLobby turns user intent into a planning-ready input before roadmap work starts.

## Mandatory Inputs

- An active ideal experience spec must exist before creating or revising a roadmap.
- If the ideal experience spec is missing, stale, contradicted, or clearly insufficient, run a requirement interview first.
- Do not begin implementation from a raw feature list alone.

## Requirement Interview Trigger

Run a requirement interview when any of the following is true.

- The project has no ideal experience spec.
- The user says the current roadmap or feature structure feels wrong.
- The long-term goal has changed.
- The team cannot explain how a feature request contributes to the intended user experience.
- Validation criteria for “did we build what the user meant?” are missing.

## Interview Coverage

Every requirement interview must cover at least these areas.

- User and operating context
- Primary frustration and current failure modes
- Ideal end-state experience
- What the user should no longer have to think about or do manually
- Boundaries between automation, suggestion, and explicit user control
- Error recovery and correction flows
- Cross-device and long-running workflow continuity
- Evidence for success and evidence for failure
- Non-goals and unacceptable tradeoffs

## Output Rule

Requirement discovery must produce or refresh these planning inputs.

- ideal experience spec
- clarified problem statement
- candidate experience pillars
- open decision questions
- validation expectations

## Validation Rule

- Every roadmap milestone must name the user-visible experience delta it is trying to create.
- Every feature candidate must explain what user problem it solves.
- Every cycle task must define how success will be validated against user intent, not only whether code runs.
