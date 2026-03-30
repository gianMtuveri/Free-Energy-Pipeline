import re
import subprocess
from pathlib import Path

import pandas as pd

from .config import AnalysisConfig
from .exceptions import MissingPoseFileError, ProdigyExecutionError, ProdigyParseError


BINDING_PATTERNS = [
    re.compile(r"Predicted binding affinity.*?:\s*([-+]?\d*\.?\d+)"),
    re.compile(r"Binding affinity.*?:\s*([-+]?\d*\.?\d+)"),
    re.compile(r"DG.*?:\s*([-+]?\d*\.?\d+)"),
]

KD_PATTERNS = [
    re.compile(r"Predicted dissociation constant.*?:\s*([0-9eE\.\-\+]+)"),
    re.compile(r"Kd.*?:\s*([0-9eE\.\-\+]+)"),
]


def _pose_path(config: AnalysisConfig, pose_id: int) -> Path:
    if config.poses_dir is None:
        raise ValueError("config.poses_dir is required.")
    return config.poses_dir / config.pose_filename_template.format(pose_id=pose_id)


def extract_haddock_electrostatic_component(pose_file: Path) -> float:
    """
    Notebook-faithful extraction of the electrostatic component from a HADDOCK PDB.

    The original notebook searched for the line containing 'energies' and used:
        line.split()[8][:-1]

    We reproduce that logic here, but cast safely to float.
    """
    with open(pose_file, "r", encoding="utf-8") as handle:
        for line in handle:
            if "energies" in line:
                parts = line.split()
                if len(parts) < 9:
                    raise ProdigyParseError(
                        f"Found 'energies' line in {pose_file}, but it has too few fields: {line.strip()}"
                    )

                raw_value = parts[8].rstrip(",;")
                try:
                    return float(raw_value)
                except ValueError as exc:
                    raise ProdigyParseError(
                        f"Could not parse electrostatic component from {pose_file}: {raw_value}"
                    ) from exc

    raise ProdigyParseError(
        f"No line containing 'energies' was found in {pose_file}"
    )


def _run_prodigy_on_pose(
    pose_file: Path,
    electrostatic_component: float,
    config: AnalysisConfig,
) -> str:
    cmd = [
        config.prodigy_executable,
        "-c",
        "A",
        "B:LIG",
        "-i",
        str(pose_file),
        "-e",
        str(electrostatic_component),
        *config.prodigy_extra_args,
    ]

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.run_prodigy_timeout,
            check=False,
        )
    except Exception as exc:
        raise ProdigyExecutionError(
            f"Failed to execute PRODIGY on {pose_file}: {exc}"
        ) from exc

    if completed.returncode != 0:
        raise ProdigyExecutionError(
            f"PRODIGY failed for {pose_file}.\n"
            f"Return code: {completed.returncode}\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )

    return completed.stdout


def _parse_prodigy_output(stdout: str) -> tuple[float | None, float | None]:
    binding = None
    kd = None

    for pattern in BINDING_PATTERNS:
        match = pattern.search(stdout)
        if match:
            binding = float(match.group(1))
            break

    for pattern in KD_PATTERNS:
        match = pattern.search(stdout)
        if match:
            kd = float(match.group(1))
            break

    if binding is None and kd is None:
        raise ProdigyParseError(
            "Could not parse binding affinity or Kd from PRODIGY output."
        )

    return binding, kd


def run_prodigy_scoring(config: AnalysisConfig) -> pd.DataFrame:
    """
    Notebook-faithful PRODIGY-LIG scoring.

    For each selected pose:
    - extract HADDOCK electrostatic component from the PDB
    - run prodigy_lig with: -c A B:LIG -i <pose> -e <electrostatic>
    - parse predicted binding affinity and Kd

    Output columns:
    - pose_id
    - haddock_electrostatic
    - pose_energy
    - binding_affinity_kcal_mol
    - kd_molar
    """
    if config.selected_pose_ids is None:
        raise ValueError("selected_pose_ids is required for PRODIGY scoring.")

    rows: list[dict] = []

    for pose_id in config.selected_pose_ids:
        pose_file = _pose_path(config, pose_id)
        if not pose_file.exists():
            raise MissingPoseFileError(f"Pose file not found: {pose_file}")

        electrostatic_component = extract_haddock_electrostatic_component(pose_file)

        stdout = _run_prodigy_on_pose(
            pose_file=pose_file,
            electrostatic_component=electrostatic_component,
            config=config,
        )

        binding, kd = _parse_prodigy_output(stdout)

        rows.append(
            {
                config.pose_id_col: pose_id,
                "haddock_electrostatic": electrostatic_component,
                config.pose_energy_col: binding,
                config.prodigy_binding_col: binding,
                config.prodigy_kd_col: kd,
            }
        )

        if config.prodigy_output_dir is not None:
            config.prodigy_output_dir.mkdir(parents=True, exist_ok=True)
            out_file = config.prodigy_output_dir / f"prodigy_pose_{pose_id}.txt"
            out_file.write_text(stdout, encoding="utf-8")

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(config.pose_id_col).reset_index(drop=True)

    return df
