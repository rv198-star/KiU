# Circle of Competence

## Identity
```yaml
skill_id: circle-of-competence
title: Circle of Competence
status: published
bundle_version: 0.1.0
skill_revision: 3
```

## Contract
```yaml
trigger:
  patterns:
    - user_considering_specific_investment
    - user_asking_if_understanding_is_deep_enough_to_act
  exclusions:
    - user_choosing_passive_index_fund
    - user_request_is_non_investing_decision
intake:
  required:
    - name: target
      type: entity
      description: Asset, company, or domain under consideration.
    - name: user_background
      type: structured
      description: Demonstrated exposure and depth in the target domain.
    - name: capital_at_risk
      type: number
      description: Share of net worth or portfolio at stake.
judgment_schema:
  output:
    type: structured
    schema:
      verdict: enum[in_circle, edge_of_circle, outside_circle]
      missing_knowledge: list[string]
      recommended_action: enum[proceed, study_more, decline]
  reasoning_chain_required: true
boundary:
  fails_when:
    - user_confuses_product_familiarity_with_business_understanding
    - user_describes_background_too_vaguely_to_test_depth
  do_not_fire_when:
    - user_chooses_passive_index_fund
    - user_request_is_non_investing_decision
```

## Rationale
This skill turns "stay in your circle" into a refusal protocol rather than a vibe-based humility slogan. The evaluator has to test what the user can actually explain about the business model, unit economics, industry structure, management incentives, and failure modes, then compare that demonstrated depth with the amount of capital and irreversibility at stake. If the explanation stays at product familiarity, social proof, or borrowed confidence, the correct output is `study_more` or `decline`, not a softened yes.[^anchor:circle-source-note] The dotcom refusal trace shows that saying no is a positive judgment when the knowledge gap is real, and the shared surface-familiarity evaluation shows why brand recognition is not evidence of investable understanding.[^anchor:circle-trace] [^anchor:circle-eval]

## Evidence Summary
The strongest evidence chain combines the circle source note, the dotcom refusal trace, and the shared surface-familiarity evaluation. Together they show that the skill is calibrated to reject action when explanation depth is thin, even if the story feels familiar or socially validated.[^anchor:circle-source-note] [^trace:canonical/dotcom-refusal.yaml] [^anchor:circle-eval]

## Relations
```yaml
depends_on: []
delegates_to:
  - bias-self-audit
constrained_by:
  - margin-of-safety-sizing
complements:
  - opportunity-cost-of-the-next-best-idea
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

Representative cases:
- `traces/canonical/dotcom-refusal.yaml`
- `traces/canonical/google-omission.yaml`
- `traces/canonical/crypto-rejection.yaml`

## Evaluation Summary
KiU Test is green and the full v0.1 shared evaluation corpus is now attached. The published summary covers four real-decision cases, four adversarial traps, and two OOD refusals, with the main failure mode still centered on surface familiarity masquerading as expertise. See `eval/summary.yaml`.

## Revision Summary
Revision 3 is the v0.3.1 hard-gate repair: the rationale and evidence text were densified to published quality, and the eval summary now binds the full shared corpus through release-scale glob references. See `iterations/revisions.yaml`.
