# PR — {{type}}({{scope}}): {{subject}}

<!-- The human opens the PR; this template mirrors what belongs in its description.
     Body rules follow COMMIT.md: written for the repo's history — no references to
     plans/tasks/this workspace. -->

## What
{{the change, in behavior terms}}

## Why
{{the problem it solves / the rule it enforces}}

## How
{{approach in a few bullets — only what a reviewer needs to navigate the diff}}

## Verification
- {{commands run and their results (vet/lint/tests/build; integration suite if boundaries moved)}}
- {{browser-verified? e2e? or explicitly "not verified live — why"}}

## Scope notes
{{deliberate limits, follow-ups pushed to the backlog, anything intentionally NOT done}}
