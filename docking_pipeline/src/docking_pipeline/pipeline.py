import pandas as pd

from .config import AnalysisConfig
from .contacts_protein import build_pose_residue_contact_table
from .prodigy_scoring import run_prodigy_scoring
from .merge_scores import attach_pose_scores_to_contacts
from .enthalpy import build_residue_enthalpy_table
from .entropy import build_residue_entropy_table
from .free_energy import run_free_energy_method
from .io_tables import load_pose_residue_contact_table, load_pose_score_table, save_table
from .validation import validate_pose_inputs, validate_free_energy_inputs


def build_contacts_from_pdb_pipeline(config: AnalysisConfig) -> pd.DataFrame:
    validate_pose_inputs(config)
    contact_df = build_pose_residue_contact_table(config)
    save_table(contact_df, config.output_dir / config.pose_residue_output_name)
    return contact_df


def run_prodigy_pipeline(config: AnalysisConfig) -> pd.DataFrame:
    validate_pose_inputs(config)
    score_df = run_prodigy_scoring(config)
    save_table(score_df, config.output_dir / config.prodigy_scores_output_name)
    return score_df


def build_scored_pose_residue_table_pipeline(config: AnalysisConfig) -> pd.DataFrame:
    """
    Full structural preprocessing:
    1. extract pose-residue contacts from PDBs
    2. run PRODIGY on each pose
    3. attach scores and compute reparted energy
    """
    validate_pose_inputs(config)

    contact_df = build_pose_residue_contact_table(config)
    score_df = run_prodigy_scoring(config)
    scored_df = attach_pose_scores_to_contacts(contact_df, score_df, config)

    save_table(scored_df, config.output_dir / config.pose_residue_output_name)
    save_table(score_df, config.output_dir / config.prodigy_scores_output_name)

    return scored_df


def run_free_energy_pipeline(config: AnalysisConfig) -> dict[str, pd.DataFrame]:
    """
    Start from precomputed CSVs:
    - pose_residue_contact_file: must include pose_energy and reparted_energy
    - pose_score_file: kept for traceability / compatibility
    """
    validate_free_energy_inputs(config)

    pose_residue_df = load_pose_residue_contact_table(config)
    pose_score_df = load_pose_score_table(config)

    enthalpy_df = build_residue_enthalpy_table(
        pose_residue_df=pose_residue_df,
        config=config,
    )

    entropy_df = build_residue_entropy_table(
        pose_residue_df=pose_residue_df,
        config=config,
    )

    free_energy_df = run_free_energy_method(
        enthalpy_df=enthalpy_df,
        entropy_df=entropy_df,
        config=config,
    )

    save_table(enthalpy_df, config.output_dir / config.enthalpy_output_name)
    save_table(entropy_df, config.output_dir / config.entropy_output_name)
    save_table(free_energy_df, config.output_dir / config.free_energy_output_name)

    return {
        "pose_scores": pose_score_df,
        "pose_residue_contacts": pose_residue_df,
        "enthalpy": enthalpy_df,
        "entropy": entropy_df,
        "free_energy": free_energy_df,
    }
