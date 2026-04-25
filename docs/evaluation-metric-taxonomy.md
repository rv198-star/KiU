# Evaluation Metric Taxonomy

v0.7.3 separates KiU evaluation into three score classes plus one evidence-confidence layer. The goal is to stop treating internal method conformance as proof of final user value.

## Class A: Method Integrity

Class A answers: does this artifact follow KiU's intended method, architecture, and absorbed reference methodology?

Class A is important, but it is not final user value. A high Class A score says the artifact is shaped correctly according to KiU's internal method. It does not prove the artifact helps a real user make a better decision.

| Metric | Class | Answers | Does Not Prove | Current Evidence Level |
| --- | --- | --- | --- | --- |
| `kiu_foundation_retained_100` | `method_integrity` | Whether KiU bundle structure, validation, installability, and production gates remain intact. | Real user value, source fidelity by itself, or external preference. | `internal_static_check` |
| `graphify_core_absorbed_100` | `method_integrity` | Whether graph substrate ideas such as provenance, tri-state structure, communities, and graph reports are represented. | That graph signals produce high-value skills. | `internal_static_check` |
| `cangjie_core_absorbed_100` | `method_integrity` | Whether observable cangjie-like production-method capabilities are structurally represented. | That KiU equals or beats cangjie in real usage. | `internal_static_check` |
| `cangjie_core_evidence_in_this_run_100` | `method_integrity` | Whether a specific run contains the evidence needed for cangjie-methodology claims. | External cangjie closure or human preference. | `internal_static_check` |
| `cangjie_methodology_internal_100` | `method_integrity` | Whether KiU's internal benchmark sees the cangjie methodology components as present. | External blind quality or real-world value. | `internal_static_check` |
| `cangjie_methodology_external_blind_100` | `method_integrity` with external evidence dependency | Whether blind reviewer evidence exists for cangjie-style comparison. | Internal method completeness when absent. | `external_blind_review` when populated, otherwise `not_available` |
| `cangjie_methodology_closure_100` | `method_integrity` with closure gate | Whether internal and required external gates are closed together. | Any underlying dimension if one required gate is missing. | Depends on all required gates |
| `cangjie_methodology_quality_100` | `method_integrity` | Whether the generated artifacts exhibit quality signals associated with cangjie-style methodology. | Real user preference or source safety. | `internal_proxy_scenario` |
| `world_context_depth_score` | `method_integrity` | Whether isolated world-context modeling has depth rather than generic pressure text. | That world context improved the artifact's final action value. | `internal_proxy_scenario` |
| `source_fit_score` | `method_integrity` | Whether a world/application pressure is relevant to the source-derived skill. | That the pressure should be applied. | `internal_proxy_scenario` |
| `dilution_risk_score` | `method_integrity` | Whether a proposed context layer risks diluting the source concept. | That the source itself is correct or useful. | `internal_proxy_scenario` |
| `compatibility_regression_risk` | `method_integrity` | Whether new mechanisms appear to break historical baselines. | That new outputs add value. | `internal_regression` |

## Class B: Source and Fact Safety

Class B answers: did the artifact avoid distorting the source, polluting source artifacts, or inventing facts?

Class B is a floor, not a bonus. A Class B failure blocks release-quality claims even when Class A or Class C appears strong.

| Metric | Class | Answers | Does Not Prove | Current Evidence Level |
| --- | --- | --- | --- | --- |
| `source_fidelity_preserved` | `source_fact_safety` | Whether source-derived claims remain faithful and are not rewritten by world layers. | Action value. | `internal_static_check` |
| `source_pollution_errors` | `source_fact_safety` | Whether external world or live-fact material leaked into source `SKILL.md` artifacts. | Source completeness or user value. | `internal_static_check` |
| `hallucination_risk_score` | `source_fact_safety` | Whether a prompt or output risks unsupported current-world or source claims. | That all facts are exhaustively correct. | `internal_proxy_scenario` or `live_fact_verification` |
| `extraction_kind` | `source_fact_safety` | Whether a graph signal is `EXTRACTED`, `INFERRED`, or `AMBIGUOUS`. | That downstream skill use is valuable. | `internal_static_check` |
| `claim_ledger` | `source_fact_safety` | Which current-world claims require verification before application. | That the verified claim is sufficient for advice. | `live_fact_verification` |
| `external_fact_pack` | `source_fact_safety` | Which bounded external facts were retrieved with source metadata. | That external facts should rewrite source skills. | `live_fact_verification` |
| `freshness_gate` | `source_fact_safety` | Whether application advice is gated by current-fact status. | Domain-expert correctness. | `live_fact_verification` |

## Class C: Action Value

Class C answers two related questions:

- `skill_action_value`: did a generated skill move the user into a better judgment or action state?
- `book_to_skill_action_coverage`: did the book-to-artifact conversion cover the source book's expected action value across published skills, workflow candidates, gateways, and explicit caveats?

Class C uses the recursive five-step method from `AGENTS.md`. A high-value artifact may help the user discover a signal, define a problem, resolve a problem into action, reject unsafe action, route to workflow, or create a feedback loop. It does not need to force every request into an action list.

| Metric | Class | Answers | Does Not Prove | Current Evidence Level |
| --- | --- | --- | --- | --- |
| `usage_outputs` | `action_value_auxiliary` | Whether generated usage scenarios pass trigger, anti-trigger, and basic output checks. | Deep action value or real-user preference. | `internal_proxy_scenario` |
| `proxy_usage_outputs` | `action_value_auxiliary` | Whether broader generated prompts expose trigger, boundary, and verdict behavior. | Human preference or domain expert validation. | `internal_proxy_scenario` |
| `practical_effect_outputs` | `action_value_auxiliary` | Whether usage and proxy signals combine into a capped practical-effect proxy. | Real product impact. | `internal_proxy_scenario` |
| `artifact_value_score` | `action_value_auxiliary` | Manual internal judgment of artifact usefulness, boundaries, and non-dilution. | External validation. | `internal_manual_review` |
| `book_to_skill_action_coverage_100` | `action_value` | Whether the source book's expected action value is covered by generated skills, workflow candidates, gateways, and named caveats. | That every individual skill is high-value or that real users prefer the output. | `internal_manual_review` or stronger |
| `workflow_action_value_status` | `action_value_auxiliary` | Whether workflow-heavy book knowledge is represented as auditable workflow candidates rather than hidden inside thick skills. | Thick skill action value. | `internal_static_check` |
| `skill_action_value_average_100` | `action_value` | Average action value of published `SKILL.md` artifacts. | Book-level coverage. | Must disclose underlying evidence level |
| `action_layer_fit_100` | `action_value` | Whether the skill knows which action-value layer it should serve. | The quality of that layer by itself. | `internal_proxy_scenario` |
| `signal_discovery_value_100` | `action_value` | Whether the skill helps convert world noise into restatable, locatable, reproducible signals. | Problem definition or execution quality. | `internal_proxy_scenario` |
| `problem_definition_value_100` | `action_value` | Whether the skill helps convert a signal into a falsifiable, measurable problem. | That a solution is already known. | `internal_proxy_scenario` |
| `action_resolution_value_100` | `action_value` | Whether the skill helps convert a defined problem into executable actions. | That the user will execute correctly. | `internal_proxy_scenario` |
| `feedback_calibration_value_100` | `action_value` | Whether the skill creates logs, pre-mortems, hit-rate ledgers, or hypothesis loops for recalibration. | That the feedback has already occurred. | `internal_proxy_scenario` |
| `comparative_decision_lift_100` | `action_value` | Whether skill-assisted output is better than baseline or reference output for decision quality. | Real-user preference unless externally reviewed. | `same_book_reference_comparison` or `internal_proxy_scenario` |
| `action_value_score_100` | `action_value` | Overall internal action-value proxy after layer fit, primary layer value, comparative lift, and feedback/boundary value. | Real-world value closure. | Must disclose underlying evidence level |

## Evidence Confidence Layer

Every Class A, B, or C metric must carry an evidence level. The evidence level determines claim strength.

| Evidence Level | Meaning | Allowed Claim | Not Allowed Claim |
| --- | --- | --- | --- |
| `internal_static_check` | Deterministic structural, schema, or file inspection evidence. | Structure is present or absent. | User value is proven. |
| `internal_regression` | Automated regression tests or compatibility replay. | The tested behavior did not regress under known cases. | General quality is proven. |
| `internal_proxy_scenario` | Generated or curated internal prompts and scoring. | Internal proxy behavior improved or passed. | Human preference is proven. |
| `internal_manual_review` | Project-internal qualitative artifact review. | Internal reviewer judged value under stated criteria. | External validation is proven. |
| `same_book_reference_comparison` | Same-book or same-source comparison against a separate baseline/reference pipeline. | Relative proxy comparison under defined scenario set. | Real-world superiority. |
| `live_fact_verification` | Bounded current-fact retrieval and cited-source verification. | A specific current-world claim was checked under bounded retrieval. | Exhaustive factual correctness. |
| `external_blind_review` | Anonymous third-party preference or quality review. | External blind evidence exists for tested artifacts. | Long-term user outcome. |
| `real_user_validation` | Real users use the skill in actual tasks. | Real usage evidence exists for tested tasks. | Domain correctness outside the observed tasks. |
| `domain_expert_review` | Expert assessment for a domain-sensitive artifact. | Expert-reviewed quality under stated scope. | Universal correctness. |

## Release Interpretation Rules

- A high Class A score means KiU's internal method is intact, not that the final skill is valuable.
- A high Class B score means the artifact is safer and more faithful, not that it is useful.
- A high Class C score can claim internal action-value evidence only at its stated evidence level.
- Class C cannot pass if Class B fails on source pollution, source fidelity, or unsafe hallucination risk.
- Class C cannot be used to hide workflow-vs-agentic boundary drift. Deterministic high-certainty workflows still belong in `workflow_candidates/`, not published `bundle/skills/`.
- External validation remains condition-dependent and must not be implied by internal proxy scores.
