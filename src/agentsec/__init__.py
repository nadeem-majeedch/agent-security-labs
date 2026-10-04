"""AgentSec Lab - the implementation behind the Agent Security Labs.

An offline, deterministic educational agent-security laboratory: a small agent
loop runs against a scripted model fixture and in-memory tools, every tool call
passes through the mediated ToolGateway, and each run writes a readable JSONL
trace. The core data models, trace schema/validation/recording, redaction, the
minimal PolicyEngine, the read-only descriptive evaluator, the one-run
experiment runner, the CLI and the declarative scenario layer live here; the
eight student labs (LAB-00 to LAB-07) are repository content under ``labs/``.

There are deliberately no real model adapters and no defences yet - the
adversarial labs observe behaviour only.

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

__version__ = "0.2.0"

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
