import pandas as pd

from .config import AnalysisConfig


def build_residue_enthalpy_table(
    pose_residue_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    """
    Notebook-faithful residue enthalpy aggregation.

    In the notebook:
    - each pose score is equally repartitioned across all contacted residues
    - for each residue, the mean of these reparted values is taken across poses
    """
    grouped = (
        pose_residue_df.groupby(config.residue_id_col, as_index=False)
        .agg(
            avg_enthalpy=(config.reparted_energy_col, "mean"),
            n_pose_contacts=(config.pose_id_col, "size"),
            n_unique_poses=(config.pose_id_col, "nunique"),
            mean_pose_energy=(config.pose_energy_col, "mean"),
        )
        .sort_values(config.residue_id_col)
        .reset_index(drop=True)
    )

    return grouped
