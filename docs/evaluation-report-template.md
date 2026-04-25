# Evaluation Report Template

Use this template for release evidence and generated-run reviews after v0.7.3. The purpose is to separate internal method correctness, source/fact safety, and action value instead of collapsing them into one ambiguous quality score.

## 1. Scope and Evidence Level

| Field | Value |
| --- | --- |
| Report id | `<report-id>` |
| Version | `<version>` |
| Samples | `<sample-list>` |
| Evidence level | `internal_static_check` / `internal_proxy_scenario` / `same_book_reference_comparison` / `external_blind_review` / `real_user_validation` / `domain_expert_review` |
| External validation claimed | `yes` / `no` |

Required statement:

```text
This report's strongest claim is limited to <evidence level>. It must not be read as stronger validation unless an external evidence level is explicitly present.
```

## 2. Method Integrity Score

Class A answers whether KiU's method and architecture are intact.

| Metric | Score / Status | Evidence Level | Interpretation | Limit |
| --- | --- | --- | --- | --- |
| `kiu_foundation_retained_100` | `<value>` | `<level>` | `<meaning>` | Does not prove action value. |
| `graphify_core_absorbed_100` | `<value>` | `<level>` | `<meaning>` | Does not prove final user value. |
| `cangjie_core_absorbed_100` | `<value>` | `<level>` | `<meaning>` | Does not prove cangjie victory. |
| `world_context_depth_score` | `<value>` | `<level>` | `<meaning>` | Does not prove world context helped. |

Decision:

```text
Method integrity: PASS / WARN / FAIL
```

## 3. Source and Fact Safety Score

Class B answers whether the artifact preserves source fidelity and fact safety.

| Metric | Score / Status | Evidence Level | Interpretation | Release Gate |
| --- | --- | --- | --- | --- |
| `source_fidelity_preserved` | `<value>` | `<level>` | `<meaning>` | Blocking |
| `source_pollution_errors` | `<value>` | `<level>` | `<meaning>` | Blocking |
| `hallucination_risk_score` | `<value>` | `<level>` | `<meaning>` | Blocking when unsafe |
| `extraction_kind` coverage | `<value>` | `<level>` | `<meaning>` | Diagnostic |

Decision:

```text
Source/fact safety: PASS / WARN / FAIL
```

Class C must not pass when Class B fails on a blocking gate.

## 4. Action Value Score

Class C answers whether the book-to-artifact conversion and individual generated skills help users discover signals, define problems, resolve problems into action, route to workflows, or calibrate feedback.

### Book-to-Skill Action Value Map

Every book-level C report must first explain what the source book is expected to contribute in action-value terms.

| Book | Generated Artifact | Source Anchor / Source Area | Book Knowledge Converted | Primary C Layer | Why This Artifact Exists |
| --- | --- | --- | --- | --- | --- |
| `<book>` | `<skill-or-workflow>` | `<source-anchor>` | `<book-knowledge>` | `<layer>` | `<reason>` |

Book-level coverage:

| Metric | Score / Status | Evidence Level | Interpretation | Limit |
| --- | --- | --- | --- | --- |
| `book_to_skill_action_coverage_100` | `<value>` | `<level>` | `<meaning>` | Does not prove every individual skill is strong. |
| `skill_action_value_average_100` | `<value>` | `<level>` | `<meaning>` | Does not prove book-level breadth. |
| `workflow_action_value_status` | `<value>` | `<level>` | `<meaning>` | Does not count as thick skill value. |

### Per-Skill Action Value

| Metric | Score / Status | Evidence Level | Interpretation | Limit |
| --- | --- | --- | --- | --- |
| `action_layer_fit_100` | `<value>` | `<level>` | `<meaning>` | Does not prove quality alone. |
| `signal_discovery_value_100` | `<value>` | `<level>` | `<meaning>` | Applies when the primary layer is discovery. |
| `problem_definition_value_100` | `<value>` | `<level>` | `<meaning>` | Applies when the primary layer is definition. |
| `action_resolution_value_100` | `<value>` | `<level>` | `<meaning>` | Applies when the primary layer is resolution. |
| `feedback_calibration_value_100` | `<value>` | `<level>` | `<meaning>` | Applies when uncertainty requires feedback. |
| `comparative_decision_lift_100` | `<value>` | `<level>` | `<meaning>` | Requires baseline/reference context. |
| `action_value_score_100` | `<value>` | `<level>` | `<meaning>` | Does not prove real-user value unless evidence level supports it. |

Decision:

```text
Action value: PASS / WARN / FAIL
```

## 5. Claim Boundary

Allowed claims:

- Method integrity is present only when Class A passes.
- Source/fact safety is present only when Class B blocking gates pass.
- Internal action value is present only when Class C passes at `internal_proxy_scenario`, `internal_manual_review`, or stronger evidence level.
- External action value is present only when `external_blind_review`, `real_user_validation`, or `domain_expert_review` exists.

Disallowed claims:

- A high Class A score proves final user value.
- A high Class B score proves usefulness.
- Internal proxy Class C proves real-user value.
- Cangjie-style method absorption proves same-source cangjie victory.
- World context depth proves world context improved the output.

## 6. Failure Modes

| Failure Mode | Class | Meaning | Required Response |
| --- | --- | --- | --- |
| Method drift | A | The artifact no longer follows KiU architecture or absorbed method. | Fix method or reduce claim. |
| Source distortion | B | The artifact misstates or rewrites source evidence. | Block release claim. |
| Source pollution | B | World/live/reference context leaked into source artifacts. | Block release claim. |
| Unsafe hallucination | B | Current-world or source claim is unsupported. | Block or caveat application. |
| Wrong action layer | C | The skill forces execution when discovery/definition/calibration is appropriate. | Reduce C score and fix action-layer fit. |
| No decision lift | C | The skill is method-rich but does not improve judgment over baseline. | Do not claim action value. |
| Workflow boundary drift | A/C | Deterministic workflow is promoted as agentic skill. | Route to `workflow_candidates/`. |

## v0.7.3 Release Claim Boundary

v0.7.3 can claim:

- KiU evaluation metrics are classified into method integrity, source/fact safety, action value, and evidence confidence.
- C-class action-value metrics are defined from the recursive five-step method.
- Existing v0.7.2 evidence has been retrofitted into the new taxonomy.
- Default generation behavior is not changed by the taxonomy.

v0.7.3 cannot claim:

- Real-user action value is proven.
- External blind preference is proven.
- Domain-expert validation is proven.
- All generated skills produce high-value advice.
- World alignment universally enriches low-temporal thought artifacts.
