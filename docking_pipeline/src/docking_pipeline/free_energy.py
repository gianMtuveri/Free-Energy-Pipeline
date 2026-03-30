import pandas as pd

from .config import AnalysisConfig
from .exceptions import UnknownFreeEnergyMethodError


def compute_notebook_basic(
    enthalpy_df: pd.DataFrame,
    entropy_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    df = enthalpy_df.merge(
        entropy_df[[config.residue_id_col, "entropy_term", "pose_fraction"]],
        on=config.residue_id_col,
        how="left",
        validate="one_to_one",
    )

    df["entropy_term"] = df["entropy_term"].fillna(0.0)
    df["pose_fraction"] = df["pose_fraction"].fillna(0.0)
    df["free_energy"] = df["avg_enthalpy"] + df["entropy_term"]
    df["method"] = "notebook_basic"
    return df


def compute_notebook_basic_smoothed(
    enthalpy_df: pd.DataFrame,
    entropy_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    df = compute_notebook_basic(enthalpy_df, entropy_df, config).copy()
    df = df.sort_values(config.residue_id_col).reset_index(drop=True)

    df["free_energy"] = (
        df["free_energy"]
        .rolling(window=config.smoothing_window, center=True, min_periods=1)
        .mean()
    )
    df["method"] = "notebook_basic_smoothed"
    return df


def compute_enthalpy_only(
    enthalpy_df: pd.DataFrame,
    entropy_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    df = enthalpy_df.copy()
    df["pose_fraction"] = 0.0
    df["entropy_term"] = 0.0
    df["free_energy"] = df["avg_enthalpy"]
    df["method"] = "enthalpy_only"
    return df


FREE_ENERGY_METHODS = {
    "notebook_basic": compute_notebook_basic,
    "notebook_basic_smoothed": compute_notebook_basic_smoothed,
    "enthalpy_only": compute_enthalpy_only,
}


def run_free_energy_method(
    enthalpy_df: pd.DataFrame,
    entropy_df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    try:
        method_fn = FREE_ENERGY_METHODS[config.free_energy_method]
    except KeyError as exc:
        available = ", ".join(sorted(FREE_ENERGY_METHODS))
        raise UnknownFreeEnergyMethodError(
            f"Unknown free-energy method: {config.free_energy_method}. "
            f"Available methods: {available}"
        ) from exc

    return method_fn(enthalpy_df, entropy_df, config)
