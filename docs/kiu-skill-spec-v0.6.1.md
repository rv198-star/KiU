# KiU Skill Spec v0.6.1

## Positioning

`v0.6.1` is the Graph-to-Skill Distillation Upgrade. It does not add more graph substrate for its own sake. It makes the v0.6 Graphify-core bottom layer visible in generated skill usage behavior.

The release line is:

`provenance-rich graph -> distillation contract -> generated skill scenarios -> usage review -> reference benchmark gate`

## Design Principles

### 1. In Use First

Graph evidence only matters if it changes downstream usage quality. `graph.json`, tri-state markers, source coordinates, communities, and `GRAPH_REPORT.md` must be translated into trigger, boundary, action, or routing behavior.

### 2. Boundary Discipline Preserved

The v0.6.1 upgrade may not improve scores by moving deterministic workflow logic into `bundle/skills/`. Workflow artifacts remain under `workflow_candidates/`. A generated gateway skill is allowed only when a run would otherwise produce zero installable skills; that gateway may route to workflows but must not inline workflow steps.

### 3. External Reference Boundary Preserved

Same-source reference packs remain benchmark material only. Distillation consumes KiU source bundles and KiU graph assets, not external final `SKILL.md` outputs.

## Distillation Contract v0.1

Each generated skill candidate may include `candidate.yaml.graph_to_skill_distillation`.

Required fields:

- `schema_version = kiu.graph-to-skill-distillation/v0.1`
- `candidate_id`
- `source_graph_hash`
- `source_graph_version`
- `rules`
- `inferred_trigger_expansions`
- `ambiguous_boundary_probes`
- `source_action_transfer`
- `graph_navigation`

Required rules:

- `INFERRED` edges may expand trigger language only when live decision context is present.
- `AMBIGUOUS` nodes or edges must become `edge_case` / refusal probes, not broad trigger permissions.
- `source_location` must be translated into concrete next-action language, not left as inert metadata.
- `GRAPH_REPORT.md` may guide related-skill handoff and navigation, but it is not independent evidence.

## Scenario Mapping

`usage/scenarios.yaml` is the main user-effect surface for graph distillation.

- `INFERRED` supporting edges become `should_trigger` scenarios with `distillation_role: trigger_expansion`.
- `AMBIGUOUS` supporting nodes or edges become `edge_case` scenarios with `distillation_role: boundary_probe`.
- Every graph-derived scenario should carry `anchor_refs`, `extraction_kind`, `source_location`, `boundary_reason`, and `next_action_shape`.
- Graph-derived scenario IDs use stable prefixes: `graph-inferred-link-*` and `graph-ambiguous-boundary-*`.

## User-Facing Rendering

Generated `SKILL.md` may include a concise `Graph-to-skill distillation` note when the candidate actually consumes `INFERRED` or `AMBIGUOUS` graph signals.

The note should state:

- which graph signal is being consumed
- whether it is `INFERRED` or `AMBIGUOUS`
- the source location backing the signal
- how it changes trigger, boundary, action, or navigation

Pure graph navigation alone should not rewrite seeded high-quality evidence summaries.

## Workflow Gateway Rule

If a generated run produces one or more `workflow_script_candidate` artifacts but zero skill candidates, KiU emits one thin `workflow-gateway` skill.

The gateway contract:

- `recommended_execution_mode = llm_agentic`
- `disposition = skill_candidate`
- routes to `workflow_candidates/<id>/workflow.yaml`
- asks for missing context when routing is under-specified
- refuses to inline deterministic workflow steps as skill reasoning

This preserves installability without violating the workflow-vs-agentic boundary.

## v0.6.1 Benchmark Gate

Reference benchmark reports include:

- `generated_run.graph_to_skill_distillation`
- `scorecard.graph_to_skill_distillation_100`
- `scorecard.v061_distillation_gate`

Minimum gate:

- `graph_to_skill_distillation_100 >= 90.0`
- workflow boundary preserved
- if same-scenario usage cases exist, KiU must remain the usage winner
- if same-scenario usage cases exist, KiU weighted pass rate must not regress
- if same-scenario usage cases exist, failure tag counts must remain empty

## Honest Scope

`v0.6.1` proves that graph substrate is no longer decorative: tri-state and source-location signals are consumed by generated skills and scored by benchmark reports.

It does not claim a large final-usage lead over `cangjie-skill`. Current same-source Poor Charlie evidence shows a modest positive usage delta, while the new value is primarily in evidence-to-usage traceability and boundary-safe installability.
