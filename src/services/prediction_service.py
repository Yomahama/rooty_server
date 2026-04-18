from datetime import datetime, timedelta
import os
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
from models.watering_prediction import MoisturePoint, WateringPrediction
from models.plant import Plant
from repos.prediction_repo import PredictionRepository
from config.prediction_config import LSTMPredictionConfig, DEFAULT_LSTM_CONFIG


class PredictionService:
    def __init__(self, config: LSTMPredictionConfig = DEFAULT_LSTM_CONFIG):
        self.config = config
        self.config.validate()
        self.repo = PredictionRepository()

    def _normalize_features(self, moisture: np.ndarray, temperature: np.ndarray, lux: np.ndarray) -> np.ndarray:
        norm_cfg = self.config.normalization
        norm_moisture = (moisture - norm_cfg.moisture_min) / \
            (norm_cfg.moisture_max - norm_cfg.moisture_min)
        norm_temperature = (temperature - norm_cfg.temperature_min) / \
            (norm_cfg.temperature_max - norm_cfg.temperature_min)
        norm_lux = (lux - norm_cfg.lux_min) / \
            (norm_cfg.lux_max - norm_cfg.lux_min)
        return np.stack([norm_moisture, norm_temperature, norm_lux], axis=-1)

    def _denormalize_moisture(self, values: np.ndarray) -> np.ndarray:
        """Denormalize moisture predictions (we only predict moisture)"""
        norm_cfg = self.config.normalization
        return values * (norm_cfg.moisture_max - norm_cfg.moisture_min) + norm_cfg.moisture_min

    def get_recent(self, hours: int = 24):
        return self.repo.get_recent(hours)

    def train(self, readings: list = []) -> None:
        if readings is None:
            readings = self.repo.get_all()

        if not readings:
            raise ValueError("No readings provided for training")

        moisture = np.array([r.moisture for r in readings], dtype=float)
        temperature = np.array([r.temperature for r in readings], dtype=float)
        lux = np.array([r.lux for r in readings], dtype=float)

        if len(moisture) <= self.config.hyperparameters.sequence_length:
            raise ValueError(
                f"Insufficient data: need at least {self.config.prediction.min_training_samples} readings, got {len(moisture)}")

        features = self._normalize_features(moisture, temperature, lux)

        target_moisture = moisture[self.config.hyperparameters.sequence_length:]
        norm_cfg = self.config.normalization
        target_moisture = (target_moisture - norm_cfg.moisture_min) / \
            (norm_cfg.moisture_max - norm_cfg.moisture_min)

        x, y = [], []
        seq_len = self.config.hyperparameters.sequence_length
        for i in range(len(features) - seq_len):
            x.append(features[i:i + seq_len])
            y.append(target_moisture[i])

        x_array = np.array(x)
        y_array = np.array(y)

        hyper = self.config.hyperparameters
        model = Sequential([
            LSTM(hyper.lstm_units_1, input_shape=(hyper.sequence_length, hyper.feature_count),
                 return_sequences=True),
            LSTM(hyper.lstm_units_2),
            Dense(hyper.dense_units, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer=hyper.optimizer, loss=hyper.loss,
                      metrics=list(hyper.metrics))
        model.fit(x_array, y_array, epochs=hyper.epochs, batch_size=hyper.batch_size,
                  verbose="1", validation_split=hyper.validation_split)
        model.save(self.config.model_path)

    def predict(self, readings: list) -> list[float]:
        model = load_model(self.config.model_path)

        seq_len = self.config.hyperparameters.sequence_length
        recent_readings = readings[-seq_len:]
        if len(recent_readings) < seq_len:
            raise ValueError(
                f"Need at least {seq_len} readings for prediction, got {len(recent_readings)}")

        moisture = np.array([r.moisture for r in recent_readings], dtype=float)
        temperature = np.array(
            [r.temperature for r in recent_readings], dtype=float)
        lux = np.array([r.lux for r in recent_readings], dtype=float)

        features = self._normalize_features(moisture, temperature, lux)

        predictions = []
        current_features = features.copy()

        for _ in range(self.config.prediction.horizon_minutes):
            x = current_features[-seq_len:].reshape(
                (1, seq_len, self.config.hyperparameters.feature_count))
            next_moisture = model.predict(x, verbose=0)[0][0]  # type: ignore

            actual_moisture = float(
                self._denormalize_moisture(np.array([next_moisture]))[0])
            predictions.append(round(actual_moisture, 1))

            last_temp = current_features[-1, 1]
            last_lux = current_features[-1, 2]

            next_feature_vector = np.array(
                [next_moisture, last_temp, last_lux])
            current_features = np.vstack(
                [current_features, next_feature_vector])

        return predictions

    def get_watering_prediction(self, plant: Plant) -> WateringPrediction:
        readings = self.repo.get_recent(hours=24)

        if not os.path.exists(self.config.model_path):
            print("🔄 No model found, training for first time...")
            self.train()

        predicted = self.predict(readings)

        minutes_until_water = None
        for i, val in enumerate(predicted):
            if val < plant.moisture_min:
                minutes_until_water = i + 1
                break

        last_reading_time = datetime.fromisoformat(readings[-1].timestamp)

        return WateringPrediction(
            current_moisture=readings[-1].moisture,
            minutes_until_water=minutes_until_water,
            historical=[
                MoisturePoint(value=r.moisture, timestamp=r.timestamp)
                for r in readings
            ],
            predicted=[
                MoisturePoint(
                    value=val,
                    timestamp=(last_reading_time +
                               timedelta(minutes=i + 1)).isoformat()
                )
                for i, val in enumerate(predicted)
            ],
        )
