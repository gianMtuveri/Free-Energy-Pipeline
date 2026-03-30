import numpy as np
import pandas as pd

from .config import AnalysisConfig


def _resolve_total_pose_count(
    pose_residue_df: pd.DataFrame,
    config: AnalysisConfig,
) -> int:
    if config.total_pose_count is not None:
        return int(config.total_pose_count)

    if config.selected_pose_ids is not None:
        return len(config.selected_pose_ids)

    return int(pose_residue_df[config.pose_id_col].nunique())


def build_residue_entropy_table(
    pose_residue_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    """
    Notebook-faithful residue entropy term.

    entropy = (n_r / N) * log(1 / N)
    """
    N = _resolve_total_pose_count(pose_residue_df, config)
    if N <= 0:
        raise ValueError("Total pose count must be positive.")

    grouped = (
        pose_residue_df.groupby(config.residue_id_col, as_index=False)
        .agg(
            n_pose_contacts=(config.pose_id_col, "size"),
            n_unique_poses=(config.pose_id_col, "nunique"),
        )
        .sort_values(config.residue_id_col)
        .reset_index(drop=True)
    )

    grouped["pose_fraction"] = grouped["n_unique_poses"] / float(N)
    grouped["entropy_term"] = grouped["pose_fraction"] * np.log(1.0 / float(N))

    return grouped
