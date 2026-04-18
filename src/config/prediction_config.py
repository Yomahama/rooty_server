from dataclasses import dataclass, field


@dataclass(frozen=True)
class SensorNormalizationConfig:
    """Configuration for normalizing sensor data ranges."""
    moisture_min: float = 0.0
    moisture_max: float = 100.0
    temperature_min: float = -10.0
    temperature_max: float = 50.0
    lux_min: float = 1.0
    lux_max: float = 65535.0

    def __post_init__(self):
        """Validate configuration values."""
        if self.moisture_min >= self.moisture_max:
            raise ValueError("moisture_min must be less than moisture_max")
        if self.temperature_min >= self.temperature_max:
            raise ValueError(
                "temperature_min must be less than temperature_max")
        if self.lux_min >= self.lux_max:
            raise ValueError("lux_min must be less than lux_max")


@dataclass(frozen=True)
class LSTMHyperparameters:
    """LSTM model architecture and training hyperparameters."""
    sequence_length: int = 144  # 2.4 hours of data (144 minutes)
    feature_count: int = 3  # moisture, temperature, lux
    lstm_units_1: int = 64
    lstm_units_2: int = 32
    dense_units: int = 16
    epochs: int = 100
    batch_size: int = 32
    validation_split: float = 0.2
    optimizer: str = "adam"
    loss: str = "mse"
    metrics: tuple = ("mae",)

    def __post_init__(self):
        """Validate hyperparameters."""
        if self.sequence_length <= 0:
            raise ValueError("sequence_length must be positive")
        if self.feature_count <= 0:
            raise ValueError("feature_count must be positive")
        if not 0.0 < self.validation_split < 1.0:
            raise ValueError("validation_split must be between 0 and 1")


@dataclass(frozen=True)
class PredictionConfig:
    """Configuration for prediction behavior."""
    horizon_minutes: int = 1440  # 24 hours
    retrain_interval_hours: int = 24
    min_training_samples: int = 145  # sequence_length + 1

    def __post_init__(self):
        """Validate prediction configuration."""
        if self.horizon_minutes <= 0:
            raise ValueError("horizon_minutes must be positive")
        if self.retrain_interval_hours <= 0:
            raise ValueError("retrain_interval_hours must be positive")


@dataclass(frozen=True)
class LSTMPredictionConfig:
    """Complete configuration for LSTM-based moisture prediction."""
    model_path: str = "sensor_lstm.keras"
    normalization: SensorNormalizationConfig = field(
        default_factory=SensorNormalizationConfig)
    hyperparameters: LSTMHyperparameters = field(
        default_factory=LSTMHyperparameters)
    prediction: PredictionConfig = field(default_factory=PredictionConfig)

    def validate(self) -> None:
        """Validate the complete configuration."""
        if self.hyperparameters.sequence_length + 1 > self.prediction.min_training_samples:
            raise ValueError(
                f"min_training_samples ({self.prediction.min_training_samples}) must be greater than "
                f"sequence_length ({self.hyperparameters.sequence_length})"
            )


# Default configuration instance
DEFAULT_LSTM_CONFIG = LSTMPredictionConfig()
