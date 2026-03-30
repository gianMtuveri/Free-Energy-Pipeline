# Docking Pipeline: Residue-Level Free Energy Analysis from HADDOCK + PRODIGY-LIG

A modular and reproducible pipeline to analyze molecular docking results at the residue level.

This project refactors an exploratory notebook into a clean, configurable pipeline that:

- extracts protein–ligand contacts from docking poses  
- computes docking scores using PRODIGY-LIG  
- projects pose-level energies onto residues  
- computes residue-level enthalpy, entropy, and free energy  
- supports interchangeable free-energy formulations  

---

## Scientific Context

This pipeline was developed to analyze docking results of peptide ligands such as Angiopep-2 on large receptors such as LRP1.

The goal is to transform pose-level docking outputs into residue-resolved energetic maps that can be interpreted biologically, for example as binding hotspots, domain preferences, or recurrent interaction regions.

---

## Pipeline Overview

HADDOCK output (PDB poses)  
→ contact extraction (MDAnalysis)  
→ electrostatic term extraction (from PDB)  
→ PRODIGY-LIG scoring (uses electrostatic component)  
→ pose-residue table  
→ enthalpy (energy repartition)  
→ entropy (pose occupancy)  
→ free energy (selectable method)  

---

## Input Requirements from HADDOCK Web Server

This pipeline assumes output from the HADDOCK web server.

### Required files

Refined docking poses, for example:

```
complex_1.pdb  
complex_2.pdb  
complex_3.pdb  
```

### Critical requirement

Each PDB must contain a HADDOCK energies line, for example  

`REMARK energies ...`

This line is used to extract the electrostatic component required by PRODIGY-LIG:


`line.split()[8]`

Therefore, the formatting must remain consistent with HADDOCK outputs.

---

## External Dependencies

This pipeline requires external tools that are not installed through pip as normal Python dependencies.

### PRODIGY-LIG

PRODIGY-LIG is used to compute binding affinity from docking poses.

Repository:  
https://github.com/haddocking/prodigy-lig

### Installation

Clone and install:

```
git clone https://github.com/haddocking/prodigy-lig.git  
cd prodigy-lig  
pip install .
```

Depending on your environment, you may need a dedicated conda environment or installation from source.

### Verify installation

`prodigy_lig --help`

### PATH configuration

If the executable is not found:

`export PATH=$PATH:/path/to/prodigy_lig`

### Important note

PRODIGY-LIG is used as a command-line executable via subprocess.  
It should not be treated as a standard Python dependency in pyproject.toml.

---

## PRODIGY-LIG Integration

The pipeline runs:

`prodigy_lig -c A B:LIG -i complex_X.pdb -e <electrostatic>`

Where:

- A = protein chain  
- B:LIG = ligand specification (rename ligand residues as LIG)  
- -e = electrostatic component extracted from HADDOCK PDB  

Important:

- the electrostatic term is extracted from the PDB  
- it is passed to PRODIGY-LIG  
- it is NOT used directly in downstream analysis  

The value used downstream is the PRODIGY-LIG predicted binding affinity (ΔG).

---

## Data Model

### Pose–Residue Table

Each row represents one (pose_id, residue_id) contact.

Columns:

- pose_id  
- residue_id  
- pose_energy  
- n_contacts_in_pose  
- reparted_energy  

### Column meaning

- pose_id: identifier of the docking pose  
- residue_id: contacted protein residue  
- pose_energy: predicted binding affinity from PRODIGY-LIG  
- n_contacts_in_pose: number of contacted residues in that pose  
- reparted_energy: pose_energy divided by n_contacts_in_pose  

---

## Energy Formulation

### Enthalpy

H(r) = mean over poses of reparted_energy  

### Entropy

S(r) = (n_r / N) * log(1 / N)

Where:

- n_r = number of poses containing residue r  
- N = total number of poses  

### Free Energy

G(r) = H(r) + S(r)

---

## Available Methods

- notebook_basic  
- notebook_basic_smoothed  
- enthalpy_only  

---

## Usage

### Step 1: Extract contacts and compute PRODIGY scores

from pathlib import Path  
from docking_pipeline import AnalysisConfig, build_scored_pose_residue_table_pipeline  

config = AnalysisConfig(  
    base_dir=Path("."),  
    output_dir=Path("results"),  
    poses_dir=Path("all_poses"),  
    selected_pose_ids=[1, 2, 3, 4, 5],  
    prodigy_executable="prodigy_lig",  
)  

df = build_scored_pose_residue_table_pipeline(config)  

---

### Step 2: Run free-energy analysis

from pathlib import Path  
from docking_pipeline import AnalysisConfig, run_free_energy_pipeline  

config = AnalysisConfig(  
    base_dir=Path("."),  
    output_dir=Path("results"),  
    pose_residue_contact_file=Path("results/pose_residue_contacts.csv"),  
    pose_score_file=Path("results/prodigy_scores.csv"),  
    selected_pose_ids=[1, 2, 3, 4, 5],  
    free_energy_method="notebook_basic",  
)  

results = run_free_energy_pipeline(config)  

---

## Notebook Role

The notebook is intended for:

- visualization  
- sanity checks  
- exploration  
- comparison of methods  
- interpretation  

The core logic lives in the src/ package.

---

## Limitations

### HADDOCK dependency

- requires specific PDB formatting  
- assumes electrostatic term position is fixed  

### PRODIGY-LIG assumptions

- requires correct chain naming  
- depends on input formatting  

### Entropy model

- simplified  
- based only on pose frequency  
- ignores conformational entropy  

### Energy repartition

- uniform distribution across residues  
- ignores interaction strength and geometry  

### Contact definition

- fixed cutoff (default 8 Å)  
- no chemical specificity  

---

## Suggested Tests

### Unit tests

- enthalpy aggregation on synthetic dataset  
- entropy calculation correctness  
- method switching  
- smoothing behavior  

### Regression tests

- compare with original notebook  
- validate top-ranked residues  

### Data checks

- reparted_energy consistency  
- no missing pose_ids  
- no unexpected duplicates  

---

## Possible Error Sources

- wrong pose subset  
- mismatch between pose ids and filenames  
- missing HADDOCK energy lines  
- PRODIGY parsing differences  
- incorrect chain naming  
- residue numbering inconsistencies  
- incorrect total pose count  

---

## Future Extensions

- ligand contact analysis  
- motif/domain aggregation  
- clustering of binding modes  
- surface mapping  
- improved entropy models  
- alternative energy repartition  

---

## Repository Structure

docking_pipeline/  
├── pyproject.toml  
├── README.md  
├── src/  
│   └── docking_pipeline/  
│       ├── config.py  
│       ├── contacts_protein.py  
│       ├── prodigy_scoring.py  
│       ├── merge_scores.py  
│       ├── enthalpy.py  
│       ├── entropy.py  
│       ├── free_energy.py  
│       └── pipeline.py  
└── notebooks/  
    └── analysis.ipynb  

---

## Author

Gian Marco Tuveri  
PhD candidate in Biophysics  
University of Barcelona  

---
