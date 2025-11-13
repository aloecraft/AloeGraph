"""
- **Module:** `src/aloegraph/node/refinement.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)
"""

from typing import Callable

from aloegraph.model.base_model import Refinable, Refinement

# note: A meta_refinement is a refinement on a refinement with the exception of a commit


def fn_is_meta_refinement(r): return (r.refinement_target_type == "refinement" or (
    r.refinement_target_id and r.refinement_target_id.startswith("RF"))) and r.operation != "commit"


def apply_refinements(
    new_refinements: list[Refinement],
    state_refinements: list[Refinement],
    state_targets: list[Refinable],
    fn_target_factory: Callable[[Refinement, str], Refinable],
    id_factory: Callable[[], str],
    id_prefix: str
) -> tuple[list[Refinement], list[Refinable]]:

    updated_refinements = state_refinements[:]
    updated_targets = state_targets[:]

    for r in new_refinements:
        r.id = f"RF{id_factory()}"
        r.ordinal = id_factory() if r.ordinal == -1 else r.ordinal

    remaining_new = [
        r for r in new_refinements if not fn_is_meta_refinement(r)]
    meta_refinements = [r for r in filter(
        fn_is_meta_refinement, new_refinements)]

    for r in meta_refinements:
        match r.operation:

            case "add":
                updated_refinements.append(r)

            case "modify":
                if r.refinement_target_id:
                    updated_refinements = [(
                        setattr(r, "operation", tref.operation) or
                        setattr(r, "refinement_target_id", tref.refinement_target_id) or
                        setattr(r, "refinement_target_type", tref.refinement_target_type) or
                        r)
                        if tref.id == r.refinement_target_id else tref
                        for tref in updated_refinements]

            case "delete":
                if r.refinement_target_id:
                    updated_refinements = [
                        tref for tref in updated_refinements
                        if tref.id != r.refinement_target_id]

    # Commit existing refinements only if requested
    commit_requested = any(r.operation == "commit" for r in remaining_new)
    if commit_requested:
        # Apply staged refinements
        for r in updated_refinements:

            match r.operation:
                case "add":
                    updated_targets.append(fn_target_factory(
                        r, f"{id_prefix}{id_factory()}"))

                case "modify":
                    if r.refinement_target_id:
                        updated_targets = [
                            fn_target_factory(r, t.id)
                            if t.id == r.refinement_target_id else t
                            for t in updated_targets]

                case "delete":
                    if r.refinement_target_id:
                        updated_targets = [
                            t for t in updated_targets
                            if t.id != r.refinement_target_id]

        updated_refinements.clear()
    else:
        updated_refinements.extend(remaining_new)

    return updated_refinements, updated_targets
