# Invert the Problem

## Identity
```yaml
skill_id: invert-the-problem
title: Invert the Problem
status: published
bundle_version: 0.1.0
skill_revision: 3
```

## Contract
```yaml
trigger:
  patterns:
    - user_planning_a_high_stakes_action_path
    - user_stuck_in_complex_success_planning
  exclusions:
    - user_request_is_pure_fact_lookup
    - user_outcome_is_already_decided
intake:
  required:
    - name: objective
      type: string
      description: Outcome the user wants to achieve.
    - name: constraints
      type: list
      description: Known constraints, irreversibilities, and deadlines.
judgment_schema:
  output:
    type: structured
    schema:
      failure_modes: list[string]
      avoid_rules: list[string]
      first_preventive_action: string
  reasoning_chain_required: true
boundary:
  fails_when:
    - user_treats_inversion_as_complete_strategy_without_followup
    - input_lacks_a_concrete_objective_or_constraint_set
  do_not_fire_when:
    - user_request_is_pure_fact_lookup
    - user_outcome_is_already_decided
```

## Rationale
Inversion should not be used as decorative "think backwards" advice. The skill is a failure-enumerator that asks what conditions would reliably destroy capital, compress options, or hide the real objective before anyone optimizes a shiny plan. If the user already knows the desired action and only wants a confidence ritual, the correct move is not to generate a generic checklist but to surface the ruin path, missing objective, or irreversible downside first.[^anchor:invert-source-note] The anti-ruin trace shows the value of explicit avoid-rules, and the adversarial no-buffer evaluation shows why a forward-only thesis can look coherent while still leaving the survival constraint undefended.[^anchor:invert-trace] [^anchor:invert-eval]

## Evidence Summary
The evidence chain combines the inversion source note, the anti-ruin checklist trace, and the adversarial zero-buffer evaluation. Together they show that inversion earns its keep when it converts vague planning into explicit failure conditions and do-not-cross rules, not when it merely restates the original plan.[^anchor:invert-source-note] [^trace:canonical/anti-ruin-checklist.yaml] [^anchor:invert-eval]

## Relations
```yaml
depends_on: []
delegates_to:
  - bias-self-audit
constrained_by: []
complements:
  - margin-of-safety-sizing
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

Representative cases:
- `traces/canonical/anti-ruin-checklist.yaml`
- `traces/canonical/pilot-pre-mortem.yaml`
- `traces/canonical/airline-bankruptcy-checklist.yaml`

## Evaluation Summary
KiU Test is green and the full v0.1 shared evaluation corpus is attached. The published summary covers four real-decision cases, four adversarial traps, and two OOD refusals for inversion-style dispatch. See `eval/summary.yaml`.

## Revision Summary
Revision 3 is the v0.3.1 hard-gate repair: the rationale and evidence text now carry explicit failure-first logic with anchor refs, and the eval summary points to the full shared corpus through glob bindings. See `iterations/revisions.yaml`.
