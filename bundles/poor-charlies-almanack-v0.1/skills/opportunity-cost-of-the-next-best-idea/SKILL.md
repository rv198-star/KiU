# Opportunity Cost of the Next Best Idea

## Identity
```yaml
skill_id: opportunity-cost-of-the-next-best-idea
title: Opportunity Cost of the Next Best Idea
status: published
bundle_version: 0.1.0
skill_revision: 3
```

## Contract
```yaml
trigger:
  patterns:
    - user_comparing_new_investment_with_existing_capital_uses
    - user_considering_switching_or_redeploying_position
  exclusions:
    - no_next_best_benchmark_is_available
    - user_request_is_non_investing_decision
intake:
  required:
    - name: new_idea
      type: string
      description: The proposed new capital deployment.
    - name: next_best_existing_option
      type: string
      description: The best live alternative available right now.
    - name: switch_costs
      type: structured
      description: Taxes, friction, and foregone compounding costs.
judgment_schema:
  output:
    type: structured
    schema:
      benchmark_winner: enum[new_idea, next_best_existing_option, insufficient_information]
      benchmark_reason: string
      followup_information: list[string]
  reasoning_chain_required: true
boundary:
  fails_when:
    - user_compares_against_idle_cash_instead_of_next_best_alternative
    - no_switch_costs_or_benchmark_inputs_are_provided
  do_not_fire_when:
    - no_next_best_benchmark_is_available
    - user_request_is_non_investing_decision
```

## Rationale
This skill prevents capital allocation from being judged in isolation. Every new idea must be compared against a live next-best use of capital after tax, friction, compounding runway, and attention cost are included; otherwise the user is really comparing the new idea to cash or to nothing at all. If the benchmark is missing or obviously weaker than the current best alternative, the skill should redirect the user back to explicit ranking rather than letting novelty win by default.[^anchor:opportunity-source-note] The Costco next-best trace and the adversarial no-benchmark evaluation both show that most bad switches happen not because the new idea is terrible, but because the old alternative was never kept alive as a real comparator.[^anchor:opportunity-trace] [^anchor:opportunity-eval]

## Evidence Summary
The evidence chain ties the opportunity-cost source note to the Costco benchmark trace and the no-benchmark adversarial evaluation. Together they show that benchmark discipline is what stops story-driven redeployment and keeps the skill anchored in live alternatives rather than abstract enthusiasm.[^anchor:opportunity-source-note] [^trace:canonical/costco-next-best-idea.yaml] [^anchor:opportunity-eval]

## Relations
```yaml
depends_on:
  - circle-of-competence
delegates_to: []
constrained_by:
  - margin-of-safety-sizing
complements:
  - bias-self-audit
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

Representative cases:
- `traces/canonical/costco-next-best-idea.yaml`
- `traces/canonical/capital-switching-benchmark.yaml`
- `traces/canonical/dexter-shoe-consideration.yaml`

## Evaluation Summary
The full v0.1 evaluation corpus is attached and published. The dominant failure mode remains users evaluating a new idea against cash or vibes rather than against a live next-best benchmark. See `eval/summary.yaml`.

## Revision Summary
Revision 3 is the v0.3.1 hard-gate repair: the rationale and evidence text now make the live-benchmark contract explicit, and the eval summary binds the full shared corpus through release-scale glob references. See `iterations/revisions.yaml`.
