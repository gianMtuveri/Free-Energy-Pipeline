from pathlib import Path

import pandas as pd

from .config import AnalysisConfig
from .validation import (
    validate_pose_residue_contact_table,
    validate_pose_score_table,
)


def load_pose_residue_contact_table(config: AnalysisConfig) -> pd.DataFrame:
    if config.pose_residue_contact_file is None:
        raise ValueError("config.pose_residue_contact_file is required.")

    df = pd.read_csv(config.pose_residue_contact_file)
    validate_pose_residue_contact_table(df, config)

    if config.selected_pose_ids is not None:
        df = df[df[config.pose_id_col].isin(config.selected_pose_ids)].copy()

    return df


def load_pose_score_table(config: AnalysisConfig) -> pd.DataFrame:
    if config.pose_score_file is None:
        raise ValueError("config.pose_score_file is required.")

    df = pd.read_csv(config.pose_score_file)
    validate_pose_score_table(df, config)

    if config.selected_pose_ids is not None:
        df = df[df[config.pose_id_col].isin(config.selected_pose_ids)].copy()

    return df


def save_table(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
