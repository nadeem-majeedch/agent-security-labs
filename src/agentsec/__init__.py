"""AgentSec Lab - educational, reproducible agent-security infrastructure.

Phase A: core data models, trace schema/validation/recording, redaction, a
deterministic mock model, sandboxed tools, the mediated ToolGateway, the minimal
PolicyEngine, a small deterministic agent loop, a read-only descriptive
evaluator, a thin one-run experiment runner, a thin CLI and a declarative
scenario layer. Deliberately no real model adapters or lab material yet (see
research/14-implementation-blueprint.md).

This package makes **no research-novelty claim**; it reimplements established
concepts for teaching and reproducible experimentation.
"""

from .agent import Agent, AgentConfig, RunResult, RunStatus
from .errors import (
    AgentError,
    AgentSecError,
    ConfigError,
    EvaluationError,
    MaxStepsExceeded,
    ModelError,
    PolicyConfigError,
    PolicyDenied,
    ScenarioConfigError,
    ToolExecutionError,
    ToolValidationError,
    TraceSchemaError,
    TraceWriteError,
    UnknownTool,
    UnsupportedParameter,
)
from .eval import (
    EvaluationInput,
    EvaluationResult,
    Evaluator,
    RunOutcome,
    TraceEvaluator,
)
from .experiment import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentRunner,
    load_experiment_config,
)
from .scenarios import (
    DeclarativeScenario,
    ExpectedObservation,
    Scenario,
    ScenarioDef,
    ScenarioOutcome,
    ScenarioRegistry,
    ScenarioStatus,
    load_scenario,
)

__version__ = "0.0.1"

__all__ = [
    "__version__",
    "Agent",
    "AgentConfig",
    "RunResult",
    "RunStatus",
    "AgentError",
    "AgentSecError",
    "ConfigError",
    "EvaluationError",
    "EvaluationInput",
    "EvaluationResult",
    "Evaluator",
    "RunOutcome",
    "TraceEvaluator",
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentRunner",
    "load_experiment_config",
    "Scenario",
    "ScenarioDef",
    "ScenarioOutcome",
    "ScenarioStatus",
    "ExpectedObservation",
    "DeclarativeScenario",
    "ScenarioRegistry",
    "load_scenario",
    "ScenarioConfigError",
    "MaxStepsExceeded",
    "ModelError",
    "PolicyConfigError",
    "PolicyDenied",
    "ToolExecutionError",
    "ToolValidationError",
    "TraceSchemaError",
    "TraceWriteError",
    "UnknownTool",
    "UnsupportedParameter",
]
