from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AnalysisConfig:
    base_dir: Path
    output_dir: Path

    # Raw structural inputs
    poses_dir: Path | None = None
    pose_filename_template: str = "complex_{pose_id}.pdb"

    # Optional pose subset
    selected_pose_ids: list[int] | None = None
    total_pose_count: int | None = None

    # Protein contact extraction
    ligand_resname: str = "LIG"
    excluded_resnames: tuple[str, ...] = ("CA2",)
    protein_contact_cutoff: float = 8.0

    # PRODIGY
    prodigy_executable: str = "prodigy"
    prodigy_output_dir: Path | None = None
    prodigy_extra_args: tuple[str, ...] = ()
    run_prodigy_timeout: int = 300

    # Intermediate / analysis inputs
    pose_score_file: Path | None = None
    pose_residue_contact_file: Path | None = None

    # Column names
    pose_id_col: str = "pose_id"
    residue_id_col: str = "residue_id"
    pose_energy_col: str = "pose_energy"
    n_contacts_in_pose_col: str = "n_contacts_in_pose"
    reparted_energy_col: str = "reparted_energy"

    # PRODIGY score table columns
    prodigy_binding_col: str = "binding_affinity_kcal_mol"
    prodigy_kd_col: str = "kd_molar"

    # Free-energy method
    free_energy_method: str = "notebook_basic"
    smoothing_window: int = 5

    # Output names
    pose_residue_output_name: str = "pose_residue_contacts.csv"
    prodigy_scores_output_name: str = "prodigy_scores.csv"
    enthalpy_output_name: str = "residue_enthalpy.csv"
    entropy_output_name: str = "residue_entropy.csv"
    free_energy_output_name: str = "residue_free_energy.csv"

    metadata: dict = field(default_factory=dict)
