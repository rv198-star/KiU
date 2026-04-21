__all__ = [
    "build_candidate_baseline",
    "decide_terminal_state",
    "derive_candidate_metadata",
    "refine_bundle_candidates",
    "refine_candidate",
    "score_candidate",
    "validate_generated_bundle",
]


def __getattr__(name: str):
    if name == "build_candidate_baseline":
        from .baseline import build_candidate_baseline

        return build_candidate_baseline
    if name == "decide_terminal_state":
        from .scoring import decide_terminal_state

        return decide_terminal_state
    if name == "derive_candidate_metadata":
        from .seed import derive_candidate_metadata

        return derive_candidate_metadata
    if name == "refine_bundle_candidates":
        from .refiner import refine_bundle_candidates

        return refine_bundle_candidates
    if name == "refine_candidate":
        from .refiner import refine_candidate

        return refine_candidate
    if name == "score_candidate":
        from .scoring import score_candidate

        return score_candidate
    if name == "validate_generated_bundle":
        from .preflight import validate_generated_bundle

        return validate_generated_bundle
    raise AttributeError(name)
