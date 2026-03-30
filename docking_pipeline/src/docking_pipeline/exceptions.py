class DockingPipelineError(Exception):
    """Base pipeline exception."""


class MissingInputFileError(DockingPipelineError, FileNotFoundError):
    """Raised when a required input file is missing."""


class MissingPoseFileError(DockingPipelineError, FileNotFoundError):
    """Raised when a required pose structure file is missing."""


class InvalidPoseResidueTableError(DockingPipelineError, ValueError):
    """Raised when the pose-residue contact table is malformed."""


class InvalidScoreTableError(DockingPipelineError, ValueError):
    """Raised when a score table is malformed."""


class UnknownFreeEnergyMethodError(DockingPipelineError, ValueError):
    """Raised when an unknown free-energy method is requested."""


class ProdigyExecutionError(DockingPipelineError, RuntimeError):
    """Raised when PRODIGY fails for a pose."""


class ProdigyParseError(DockingPipelineError, ValueError):
    """Raised when PRODIGY output cannot be parsed."""
