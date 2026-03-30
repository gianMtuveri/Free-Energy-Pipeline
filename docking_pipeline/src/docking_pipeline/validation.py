from pathlib import Path

import pandas as pd

from .config import AnalysisConfig
from .exceptions import (
    MissingInputFileError,
    InvalidPoseResidueTableError,
    InvalidScoreTableError,
)


def _require_file(path: Path | None, label: str) -> None:
    if path is None:
        raise MissingInputFileError(f"Missing required path for {label}.")
    if not path.exists():
        raise MissingInputFileError(f"Required input file not found: {path}")


def _require_dir(path: Path | None, label: str) -> None:
    if path is None:
        raise MissingInputFileError(f"Missing required path for {label}.")
    if not path.exists():
        raise MissingInputFileError(f"Required directory not found: {path}")
    if not path.is_dir():
        raise MissingInputFileError(f"Expected a directory for {label}: {path}")


def validate_pose_inputs(config: AnalysisConfig) -> None:
    _require_dir(config.poses_dir, "poses_dir")


def validate_free_energy_inputs(config: AnalysisConfig) -> None:
    _require_file(config.pose_residue_contact_file, "pose_residue_contact_file")
    _require_file(config.pose_score_file, "pose_score_file")


def validate_pose_residue_contact_table(
    df: pd.DataFrame,
    config: AnalysisConfig,
) -> None:
    required = {
        config.pose_id_col,
        config.residue_id_col,
        config.n_contacts_in_pose_col,
    }
    missing = required - set(df.columns)
    if missing:
        raise InvalidPoseResidueTableError(
            f"Pose-residue contact table is missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise InvalidPoseResidueTableError("Pose-residue contact table is empty.")

    if (df[config.n_contacts_in_pose_col] <= 0).any():
        raise InvalidPoseResidueTableError(
            "n_contacts_in_pose must be strictly positive for all rows."
        )


def validate_pose_score_table(
    df: pd.DataFrame,
    config: AnalysisConfig,
) -> None:
    required = {config.pose_id_col, config.pose_energy_col}
    missing = required - set(df.columns)
    if missing:
        raise InvalidScoreTableError(
            f"Pose score table is missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise InvalidScoreTableError("Pose score table is empty.")
