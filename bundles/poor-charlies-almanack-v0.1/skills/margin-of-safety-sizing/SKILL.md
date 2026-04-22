# Margin of Safety Sizing

## Identity
```yaml
skill_id: margin-of-safety-sizing
title: Margin of Safety Sizing
status: published
bundle_version: 0.1.0
skill_revision: 3
```

## Contract
```yaml
trigger:
  patterns:
    - user_deciding_position_size_for_investment
    - user_contemplating_concentrated_capital_allocation
  exclusions:
    - user_missing_uncertainty_inputs
    - user_request_is_non_investing_decision
intake:
  required:
    - name: downside_range
      type: structured
      description: Estimated downside range and ruin conditions.
    - name: liquidity_profile
      type: structured
      description: Liquidity, reversibility, and access to fallback capital.
    - name: conviction_basis
      type: string
      description: Why the user believes the edge exists.
judgment_schema:
  output:
    type: structured
    schema:
      sizing_band: enum[tiny, small, medium, concentrated, refuse]
      constraints: list[string]
      rationale: string
  reasoning_chain_required: true
boundary:
  fails_when:
    - user_asserts_high_conviction_without_downside_math
    - liquidity_or_ruin_inputs_are_missing
  do_not_fire_when:
    - user_request_is_non_investing_decision
    - user_missing_uncertainty_inputs
```

## Rationale
This skill makes margin of safety operational at the sizing layer rather than leaving it trapped inside valuation talk. The evaluator must ask how wrong the thesis can be, how quickly liquidity can disappear, and whether leverage or irreversibility can turn a recoverable mistake into ruin. If the downside path includes forced selling, refinancing dependence, or zero cash buffer, the correct answer is to cut size or decline the bet even when the upside narrative still sounds compelling.[^anchor:margin-source-note] The Salomon exposure-cap trace and the no-buffer adversarial evaluation both show that survival comes from limiting exposure before certainty arrives, not from averaging down after the balance sheet has already lost flexibility.[^anchor:margin-trace] [^anchor:margin-eval]

## Evidence Summary
The bundle anchors this skill to the margin source note, the Salomon exposure-cap trace, and the zero-buffer adversarial case. Together they tie sizing discipline to survival, liquidity, and balance-sheet resilience instead of treating margin of safety as a purely verbal comfort phrase.[^anchor:margin-source-note] [^trace:canonical/salomon-exposure-cap.yaml] [^anchor:margin-eval]

## Relations
```yaml
depends_on:
  - circle-of-competence
delegates_to: []
constrained_by:
  - invert-the-problem
complements:
  - opportunity-cost-of-the-next-best-idea
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

Representative cases:
- `traces/canonical/sees-candies-discipline.yaml`
- `traces/canonical/salomon-exposure-cap.yaml`
- `traces/canonical/irreversible-bet-precheck.yaml`

## Evaluation Summary
The full v0.1 evaluation corpus is attached and published. The dominant failure mode remains users presenting conviction without downside, liquidity, or ruin math. See `eval/summary.yaml`.

## Revision Summary
Revision 3 is the v0.3.1 hard-gate repair: the rationale and evidence text now spell out survival-first sizing logic, and the eval summary binds the full shared corpus through release-scale glob references. See `iterations/revisions.yaml`.
