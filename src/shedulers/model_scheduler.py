import time
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config.prediction_config import LSTMPredictionConfig
from services.prediction_service import PredictionService


class ModelTrainingScheduler:
    def __init__(self):
        self.prediction_service = PredictionService()
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def start_scheduler(self):
        if self.is_running:
            return

        # Schedule daily retraining at 2 AM
        self.scheduler.add_job(
            self.daily_retrain,
            CronTrigger(hour=2, minute=0),
            id='daily_retrain',
            name='Daily Model Retraining',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True

    def stop_scheduler(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False

    def daily_retrain(self):
        try:
            self.prediction_service.train()
        except Exception as e:
            print(f"❌ Unexpected error during retraining: {e}")
            raise

    def get_model_status(self) -> dict:
        if not os.path.exists(LSTMPredictionConfig.model_path):
            return {
                "exists": False,
                "age_hours": None,
                "last_trained": None,
                "needs_retraining": True
            }

        model_mtime = os.path.getmtime(LSTMPredictionConfig.model_path)
        age_seconds = time.time() - model_mtime
        age_hours = age_seconds / 3600

        return {
            "exists": True,
            "age_hours": round(age_hours, 1),
            "last_trained": datetime.fromtimestamp(model_mtime).isoformat(),
            "needs_retraining": age_hours >= 24
        }


model_scheduler = ModelTrainingScheduler()
