# Action Value Metrics

v0.7.3 defines Class C evaluation as `action_value`. It measures whether a KiU skill moves the user into a better judgment or action state under the recursive five-step method.

Class C is not a synonym for `usage_outputs`, action-list verbosity, or practical-looking prose. A skill has action value when it helps the user discover a signal, define a problem, resolve a problem into action, refuse unsafe action, ask for missing context, or create feedback calibration.

Class C has two evaluation levels:

- `skill_action_value`: whether a single generated `SKILL.md` has action value.
- `book_to_skill_action_coverage`: whether the book's expected action value is covered by the generated skills, workflow candidates, gateways, and explicit caveats.

Both levels are required for book-to-skill evaluation. A run can have high `skill_action_value` for its published skills while still having weak `book_to_skill_action_coverage` if the book contains important action-value areas that were not converted into skills or workflow candidates.

## Foundation

The recursive five-step method has four action-value layers:

| Layer | Transition | Successful Output |
| --- | --- | --- |
| `signal_discovery` | world -> signal | A signal that can be restated, located, and reproduced. |
| `problem_definition` | signal -> problem | A falsifiable and measurable problem statement. |
| `action_resolution` | problem -> action | Executable actions with inputs, outputs, acceptance criteria, and stop conditions. |
| `feedback_calibration` | execution -> recalibration | A decision log, pre-mortem, hit-rate ledger, hypothesis ledger, or reroute to L1/L2/L3. |

A skill may be high-value at any layer. Historical, philosophical, and principle-heavy skills often create value by defining problems or calibrating feedback rather than by giving direct action instructions.

## Core Metrics

### `book_to_skill_action_coverage_100`

Measures whether a source book's expected action value is covered by the generated artifacts.

Required evidence:

- The report states the book's action-value expectation before scoring individual skills.
- The report lists generated `bundle/skills/`, `workflow_candidates/`, gateways, and filtered candidates separately.
- Each published skill is mapped to a source anchor and a book knowledge unit.
- Workflow-heavy knowledge is credited as workflow action value only when it remains auditable under `workflow_candidates/` or through a gateway; it must not be counted as thick skill value.
- Missing book-level action-value areas are named explicitly.

Scoring criteria:

- `90-100`: The generated skills and workflow candidates cover the book's primary action-value areas with clear source anchors and no boundary drift.
- `70-89`: The main action-value areas are covered, but breadth, workflow coverage, or source-anchor strength has visible gaps.
- `40-69`: Some good skills exist, but large parts of the book's expected action value are absent or only weakly represented.
- `0-39`: The run produces isolated useful artifacts but does not represent the book's action-value profile.

Failure examples:

- Scoring three good skills as if they represented the whole book while ignoring missing workflow-heavy chapters.
- Counting workflow candidates as published skills.
- Giving book-level action-value credit without source anchors.
- Treating filtered pseudo-skills as covered action value.

### `action_layer_fit_100`

Measures whether the skill serves the right action-value layer for the source material and user request.

Scoring criteria:

- `90-100`: The skill clearly identifies its primary layer and avoids forcing itself into a wrong layer.
- `70-89`: The primary layer is mostly right, but the output mixes in weaker adjacent-layer behavior.
- `40-69`: The skill produces useful text but does not understand whether it is discovering, defining, resolving, or calibrating.
- `0-39`: The skill applies the wrong layer, such as turning a philosophical reflection into direct operational advice or turning a deterministic checklist into an agentic judgment skill.

Failure examples:

- A low-temporal principle skill forces live-world pressure into the answer even when the user asks for conceptual understanding.
- A high-certainty workflow gets published as a thick skill instead of being routed to `workflow_candidates/`.
- A historical analogy skill gives direct advice without checking whether the analogy is transferable.

### `signal_discovery_value_100`

Measures whether the skill helps users discover meaningful signals from noisy context.

Required evidence:

- It establishes a baseline or normal state.
- It states the target, expectation, or healthy pattern.
- It identifies a gap, anomaly, risk, opportunity, or weak signal.
- It gives observation actions rather than premature solutions.
- The signal can be restated, located, and reproduced.

### `problem_definition_value_100`

Measures whether the skill turns a signal into a falsifiable and measurable problem.

Required evidence:

- It distinguishes symptom, cause, constraint, and conclusion.
- It asks why-chain, first-principles, or jobs-to-be-done style questions when appropriate.
- It avoids turning user preference or stance into the problem statement.
- It names a falsifiable problem.
- It proposes at least one measurement or disconfirmation criterion.

### `action_resolution_value_100`

Measures whether the skill turns a defined problem into executable action.

Required evidence:

- It restates the current baseline and target state.
- It identifies the actionable gap.
- It chooses a strategy or presents explicit tradeoffs.
- It breaks the next step into input, output, owner or agent, timing, acceptance criteria, and stop condition where applicable.
- It avoids over-action when context is insufficient.

### `feedback_calibration_value_100`

Measures whether the skill creates a feedback loop for uncertain decisions.

Required evidence:

- It records key assumptions.
- It recommends a decision log, pre-mortem, hit-rate ledger, or hypothesis ledger when uncertainty matters.
- It states what evidence would disconfirm the recommendation.
- It explains which layer to revisit after feedback: signal discovery, problem definition, or action resolution.
- It avoids treating one answer as final when the situation is uncertain.

### `comparative_decision_lift_100`

Measures whether skill-assisted output improves decision quality over a baseline or reference output for the same scenario.

Required evidence:

- A baseline or reference output exists for comparison.
- The KiU output lowers action uncertainty, improves problem framing, reduces unsafe action, or clarifies next steps.
- The comparison records failure modes rather than only final scores.
- The evidence level is stated: internal proxy, same-book reference, external blind, real user, or expert review.

## Aggregate Score

Recommended internal proxy formula:

```text
action_value_score_100 =
  30% action_layer_fit_100
  30% primary_layer_value_100
  20% comparative_decision_lift_100
  20% feedback_calibration_or_boundary_value_100
```

`primary_layer_value_100` is selected from:

```text
signal_discovery_value_100
problem_definition_value_100
action_resolution_value_100
feedback_calibration_value_100
```

For `multi_layer` skills, use the average of the relevant layer scores, but penalize any layer that is forced without source or context support.

`feedback_calibration_or_boundary_value_100` may use feedback calibration directly, or boundary value when the right action is refusal, deferral, or context gathering.

## Gating Rules

- Class C cannot pass when Class B fails on source fidelity, source pollution, or unsafe hallucination risk.
- Class C cannot compensate for workflow-vs-agentic boundary drift.
- Class C must not reward direct action when the correct behavior is `ask_more_context`, `apply_with_caveats`, or `refuse`.
- Class C must disclose evidence level. Internal proxy action value is not real-user validation.
- Class C must judge average behavior across scenario types, not isolated best-case brilliance.

## v0.7.3 Claim Boundary

v0.7.3 may claim that KiU now has a structured internal action-value evaluation vocabulary.

v0.7.3 may not claim that generated skills have proven real-user value, external preference, or domain-expert approval.
