from pathlib import Path

import MDAnalysis as mda
import pandas as pd

from .config import AnalysisConfig
from .exceptions import MissingPoseFileError


def _pose_path(config: AnalysisConfig, pose_id: int) -> Path:
    if config.poses_dir is None:
        raise ValueError("config.poses_dir is required.")
    return config.poses_dir / config.pose_filename_template.format(pose_id=pose_id)


def _extract_contacted_residues_for_pose(
    pose_file: Path,
    ligand_resname: str,
    cutoff: float,
    excluded_resnames: tuple[str, ...],
) -> list[int]:
    u = mda.Universe(str(pose_file))

    ligand = u.select_atoms(f"resname {ligand_resname}")
    if len(ligand) == 0:
        return []

    nearby = u.select_atoms(
        f"protein and around {cutoff} group ligand",
        ligand=ligand,
    )

    residue_ids: list[int] = []
    seen: set[int] = set()

    for residue in nearby.residues:
        if residue.resname in excluded_resnames:
            continue
        resid = int(residue.resid)
        if resid not in seen:
            seen.add(resid)
            residue_ids.append(resid)

    residue_ids.sort()
    return residue_ids


def build_pose_residue_contact_table(config: AnalysisConfig) -> pd.DataFrame:
    """
    Extract one row per (pose_id, residue_id) contact from pose PDBs.

    Output columns:
    - pose_id
    - residue_id
    - n_contacts_in_pose
    """
    if config.selected_pose_ids is None:
        raise ValueError(
            "selected_pose_ids is required for raw PDB extraction, "
            "because the original notebook operated on an explicit pose subset."
        )

    rows: list[dict] = []

    for pose_id in config.selected_pose_ids:
        pose_file = _pose_path(config, pose_id)
        if not pose_file.exists():
            raise MissingPoseFileError(f"Pose file not found: {pose_file}")

        residue_ids = _extract_contacted_residues_for_pose(
            pose_file=pose_file,
            ligand_resname=config.ligand_resname,
            cutoff=config.protein_contact_cutoff,
            excluded_resnames=config.excluded_resnames,
        )

        if not residue_ids:
            continue

        n_contacts = len(residue_ids)

        for residue_id in residue_ids:
            rows.append(
                {
                    config.pose_id_col: pose_id,
                    config.residue_id_col: residue_id,
                    config.n_contacts_in_pose_col: n_contacts,
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(
            [config.pose_id_col, config.residue_id_col]
        ).reset_index(drop=True)

    return df
