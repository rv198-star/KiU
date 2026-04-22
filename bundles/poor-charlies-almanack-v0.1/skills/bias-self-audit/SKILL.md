# Bias Self Audit

## Identity
```yaml
skill_id: bias-self-audit
title: Bias Self Audit
status: published
bundle_version: 0.1.0
skill_revision: 3
```

## Contract
```yaml
trigger:
  patterns:
    - user_about_to_commit_high_stakes_investment_decision
    - user_expressing_unusual_certainty_or_social_pressure
  exclusions:
    - decision_is_low_stakes_or_reversible
    - user_request_is_non_investing_decision
intake:
  required:
    - name: thesis
      type: string
      description: The current decision thesis in the user's own words.
    - name: incentives
      type: list
      description: Incentives, identity, or social forces that could bias the user.
    - name: reversibility
      type: string
      description: How costly it is to reverse the decision.
judgment_schema:
  output:
    type: structured
    schema:
      triggered_biases: list[string]
      severity: enum[low, medium, high]
      mitigation_actions: list[string]
  reasoning_chain_required: true
boundary:
  fails_when:
    - user_tries_to_use_bias_audit_as_domain_analysis
    - decision_is_too_low_stakes_to_warrant_full_audit
  do_not_fire_when:
    - decision_is_low_stakes_or_reversible
    - user_request_is_non_investing_decision
```

## Rationale
This skill exists to convert "watch your biases" from empty hygiene language into a required audit step before commitment. The evaluator should name the likely distortion cluster, tie it to incentives, identity, sunk cost, or social proof, and then require a concrete countermeasure such as disconfirming evidence, an outside base rate, or a reduced position. If the user cannot specify what bias is currently active, the safe assumption is that confidence has outrun self-observation.[^anchor:bias-source-note] The US Air regret trace and the shared surface-familiarity adversarial case both show that a persuasive story can hide ego, imitation, or attachment until the decision is already effectively locked in.[^anchor:bias-trace] [^anchor:bias-eval]

## Evidence Summary
The strongest evidence chain combines the bias source note, the US Air anti-pattern trace, and the adversarial familiarity case. Together they show that the skill is strongest when it forces named distortions and counter-measures before an irreversible commitment, not after the narrative has already taken over.[^anchor:bias-source-note] [^trace:canonical/us-air-regret.yaml] [^anchor:bias-eval]

## Relations
```yaml
depends_on: []
delegates_to: []
constrained_by:
  - circle-of-competence
complements:
  - invert-the-problem
  - opportunity-cost-of-the-next-best-idea
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

Representative cases:
- `traces/canonical/us-air-regret.yaml`
- `traces/canonical/incentive-caused-delusion-audit.yaml`
- `traces/canonical/pilot-pre-mortem.yaml`

## Evaluation Summary
The full v0.1 evaluation corpus is attached and published. The remaining calibration question is not whether the skill is ready to ship, but how strict later versions should become around low-stakes refusals. See `eval/summary.yaml`.

## Revision Summary
Revision 3 is the v0.3.1 hard-gate repair: the rationale and evidence text now make the audit contract explicit, and the eval summary binds the full shared corpus through release-scale glob references. See `iterations/revisions.yaml`.
