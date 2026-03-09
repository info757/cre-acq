# Story V2-8: Boundaries

Status: ready-for-dev

## Story

As a CRE professional,
I want clear documentation of what v2 handles well and what it does not,
so that I don't over-rely on the model for unsupported scenarios.

## Acceptance Criteria

1. **Given** the v2 implementation **When** boundaries are documented **Then** asset types v2 handles well are listed (office, retail, mixed-use with commercial concentration)
2. **And** scope disclaimer: "matches a targeted slice of Argus lease-level modeling"
3. **And** no "Argus replacement" claim until repeatable across 3+ real cases
4. **And** documentation is in architecture.md, prd.md, or README

## Tasks / Subtasks

- [ ] Task 1: Update architecture.md (AC: 1, 2, 3, 4)
  - [ ] Add Boundaries section with asset types
  - [ ] Add scope disclaimer
  - [ ] Add claim policy (no Argus replacement until validated)
- [ ] Task 2: Update prd.md (AC: 4)
  - [ ] Ensure FR46-FR48 reflected in PRD
  - [ ] Boundaries section or reference
- [ ] Task 3: README (optional)
  - [ ] If stage-2-valuation/v2/README.md exists, add boundaries summary
  - [ ] Link to architecture, prd

## Dev Notes

- v2-argus-lite-brief.md: "Define which asset types v2 handles well; do not claim Argus replacement until repeatable across real cases"
- Asset types: office, retail, mixed-use with meaningful commercial concentration
- Excluded or limited: multifamily (different lease structure), industrial (often simpler), land (no leases)
