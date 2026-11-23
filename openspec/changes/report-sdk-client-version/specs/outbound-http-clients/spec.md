## ADDED Requirements

### Requirement: Operators can observe the effective SDK client version

The service MUST provide a loopback-only SDK version observation for a model.
It MUST use the in-process version used to construct outgoing SDK fingerprints
and compare it with the model's advertised minimum using numeric version
components. It MUST distinguish a below-minimum version from unavailable
metadata. It MUST NOT perform inference, expose account information, or change
service readiness.

#### Scenario: A serving replica uses a below-minimum SDK version

- **WHEN** a local observer checks a model whose minimum is higher than the effective version
- **THEN** the result identifies the version as below the minimum

#### Scenario: The model minimum is missing

- **WHEN** the registry cannot supply a valid minimum for the requested model
- **THEN** the result reports the minimum as unavailable

#### Scenario: Observation from a non-loopback client

- **WHEN** a non-loopback client requests the observation
- **THEN** the request is rejected without returning model or version information
