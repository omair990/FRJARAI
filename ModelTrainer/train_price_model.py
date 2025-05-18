import os
import json
import pickle
import logging
import numpy as np
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../cloud_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def extract_features(data: dict) -> list:
    """
    Extracts 31 numerical features from pricing data.

    Args:
        data: Dictionary containing min_price, max_price, average, and median

    Returns:
        List of 31 numerical features
    """
    try:
        min_price = data.get("min_price", 0.0)
        max_price = data.get("max_price", 0.0)
        average = data.get("average", 0.0)
        median = data.get("median", average)

        # Calculate meaningful features
        price_range = max_price - min_price
        volatility = price_range / (average + 1e-5)  # Avoid division by zero
        symmetry = (average - median) / (price_range + 1e-5)
        mid_price = (min_price + max_price) / 2
        avg_min_ratio = average / (min_price + 1e-5)
        avg_max_ratio = average / (max_price + 1e-5)
        median_min_ratio = median / (min_price + 1e-5)
        median_max_ratio = median / (max_price + 1e-5)

        # Create feature vector with calculated values
        features = [
            min_price, max_price, average, median,
            price_range, volatility, symmetry,
            mid_price, avg_min_ratio, avg_max_ratio,
            median_min_ratio, median_max_ratio,
            np.log1p(min_price), np.log1p(max_price),  # Log-transformed features
            np.log1p(average), np.log1p(median)
        ]

        # Pad with zeros to ensure exactly 31 features
        while len(features) < 31:
            features.append(0.0)

        return features[:31]  # Return exactly 31 features

    except Exception as e:
        logger.error(f"Feature extraction error: {str(e)}")
        return [0.0] * 31  # Fallback to zeros if error occurs



class CloudTrainingModel:
    def __init__(self):
        self.forecast_file = "../assets/final_materials_with_forecast.json"
        self.training_file = "../assets/cloud_ai_training.json"
        self.model_file = "../models/ai_price_model.pkl"
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize directories and load/create model."""
        os.makedirs("../models", exist_ok=True)
        os.makedirs("../assets", exist_ok=True)
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Load existing model or train a new one."""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("Loaded existing model successfully")
            else:
                logger.info("No model found - training new model")
                self.train_model()
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            self.train_model()

    def train_model(self):
        """Train the pricing model."""
        try:
            # Load and prepare data
            data = self._load_data()
            if not data:
                raise ValueError("No valid data available")

            X, y = self._prepare_data(data)
            if len(X) == 0:
                raise ValueError("No valid training examples")

            # Train model
            self._train_xgboost(X, y)
            logger.info("✅ Model trained and saved successfully")

        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise

    def _load_data(self):
        """Load JSON data from file."""
        try:
            if not os.path.exists(self.forecast_file):
                logger.error(f"File not found: {self.forecast_file}")
                return None

            with open(self.forecast_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "materials" not in data:
                logger.error("Invalid data format")
                return None

            return data

        except Exception as e:
            logger.error(f"Data loading failed: {str(e)}")
            return None

    def _prepare_data(self, data):
        """Prepare training data from raw input."""
        X_numerical, y_list = [], []
        cities, categories, seasons = [], [], []

        for material in data.get("materials", []):
            city = material.get("city", "unknown").strip().lower()
            category = material.get("category", "general").strip().lower()
            margin = float(material.get("market_margin", 1.0))

            for product in material.get("products", []):
                try:
                    # Extract and validate prices
                    prices = {
                        "min_price": float(product.get("min_price", 0)),
                        "max_price": float(product.get("max_price", 0)),
                        "average": float(product.get("average", 0)),
                        "median": float(product.get("median", product.get("average", 0)))
                    }

                    if prices["min_price"] <= 0 or prices["max_price"] <= prices["min_price"]:
                        continue

                    # Calculate features and target price
                    features = extract_features(prices)
                    if not isinstance(features, list) or any(isinstance(i, list) for i in features):
                        logger.error(f"Unexpected nested structure in extracted features: {features}")
                        continue  # Skip this product if features are not a flat list

                    price = self._calculate_target_price(prices, margin)

                    X_numerical.append(features)
                    y_list.append(price)
                    cities.append(city)
                    categories.append(category)
                    seasons.append(f"Q{(datetime.now().month - 1) // 3 + 1}")

                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping product: {str(e)}")
                    continue

        X_numerical = np.array(X_numerical)
        y = np.array(y_list)

        ohe_city = OneHotEncoder(handle_unknown='ignore').fit_transform(
            np.array(cities).reshape(-1, 1)) if cities else np.empty((0, 0))
        ohe_category = OneHotEncoder(handle_unknown='ignore').fit_transform(
            np.array(categories).reshape(-1, 1)) if categories else np.empty((0, 0))
        ohe_season = OneHotEncoder(handle_unknown='ignore').fit_transform(
            np.array(seasons).reshape(-1, 1)) if seasons else np.empty((0, 0))

        # Explicitly reshape all arrays to their expected shapes
        X_numerical = X_numerical.reshape(X_numerical.shape[0], -1) if X_numerical.size > 0 else np.empty((0, 31))
        ohe_city = ohe_city.toarray() if hasattr(ohe_city, 'toarray') else ohe_city
        ohe_city = ohe_city.reshape(X_numerical.shape[0], -1) if ohe_city.size > 0 else np.empty((0, 0))
        ohe_category = ohe_category.toarray() if hasattr(ohe_category, 'toarray') else ohe_category
        ohe_category = ohe_category.reshape(X_numerical.shape[0], -1) if ohe_category.size > 0 else np.empty((0, 0))
        ohe_season = ohe_season.toarray() if hasattr(ohe_season, 'toarray') else ohe_season
        ohe_season = ohe_season.reshape(X_numerical.shape[0], -1) if ohe_season.size > 0 else np.empty((0, 0))


        logger.info(f"Shape of X_numerical: {X_numerical.shape}")
        logger.info(f"Shape of ohe_city: {ohe_city.shape}")
        logger.info(f"Shape of ohe_category: {ohe_category.shape}")
        logger.info(f"Shape of ohe_season: {ohe_season.shape}")

        if X_numerical.size > 0:
            X = np.hstack([X_numerical, ohe_city, ohe_category, ohe_season])
        else:
            X = np.concatenate([ohe_city, ohe_category, ohe_season], axis=1) if any(
                [ohe_city.size > 0, ohe_category.size > 0, ohe_season.size > 0]) else np.empty((0, 0))

        # Ensure y is 1-dimensional
        if y.ndim > 1:
            y = y.flatten()

        logger.info(f"Shape of X returned from _prepare_data: {X.shape}")
        logger.info(f"Shape of y returned from _prepare_data: {y.shape}")

        return X, y



    def _calculate_target_price(self, prices, margin):
        """Calculate target price with business logic."""
        base_price = (0.4 * prices["min_price"] +
                      0.3 * prices["median"] +
                      0.2 * prices["average"] +
                      0.1 * prices["max_price"])

        price = base_price * margin

        # Ensure price stays within bounds
        epsilon = 0.01
        price = max(min(price, prices["max_price"] - epsilon),
                    prices["min_price"] + epsilon)

        # Add slight variation if too close to average
        if abs(price - prices["average"]) < epsilon:
            price += epsilon if price < prices["max_price"] else -epsilon

        return round(price, 2)

    def _train_xgboost(self, X, y):
        """Train XGBoost model and save it."""
        logger.info(f"Shape of X just before train_test_split: {X.shape}")
        logger.info(f"Shape of y just before train_test_split: {y.shape}")


        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42
        )

        model = XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            early_stopping_rounds=10,
            eval_metric="rmse"
        )

        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=True
        )

        with open(self.model_file, "wb") as f:
            pickle.dump(model, f)

        self.model = model

    def schedule_auto_training(self, hours=6):
        """Schedule automatic retraining."""
        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                self.train_model,
                'interval',
                hours=hours,
                next_run_time=datetime.now()
            )
            scheduler.start()
            logger.info(f"⏰ Scheduled retraining every {hours} hours")
        except Exception as e:
            logger.error(f"Scheduler failed: {str(e)}")



if __name__ == "__main__":
    try:
        model = CloudTrainingModel()
        model.schedule_auto_training()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
