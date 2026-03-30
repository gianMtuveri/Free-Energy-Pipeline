import pandas as pd

from .config import AnalysisConfig


def attach_pose_scores_to_contacts(
    pose_residue_df: pd.DataFrame,
    pose_score_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    """
    Merge per-pose scores into the pose-residue contact table and compute
    reparted_energy = pose_energy / n_contacts_in_pose.
    """
    merged = pose_residue_df.merge(
        pose_score_df[[config.pose_id_col, config.pose_energy_col]],
        on=config.pose_id_col,
        how="inner",
        validate="many_to_one",
    ).copy()

    merged[config.reparted_energy_col] = (
        merged[config.pose_energy_col] / merged[config.n_contacts_in_pose_col]
    )

    return merged
