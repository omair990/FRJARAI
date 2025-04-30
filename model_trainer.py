# train_price_model.py

import json
import numpy as np
import pickle
import os
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# ✅ Load your product pricing data
with open("assets/final_materials_with_forecast.json", "r", encoding="utf-8") as f:
    data = json.load(f)

X = []
y = []

for material in data["materials"]:
    for product in material.get("products", []):
        min_price = product.get("min_price")
        max_price = product.get("max_price")
        average = product.get("average")
        median = product.get("median")
        unit = product.get("unit", "").lower()

        if all(isinstance(v, (int, float)) for v in [min_price, max_price, average, median]):
            # ⚙️ Smart internal features
            price_range = max_price - min_price
            mid_diff = average - median
            range_ratio = price_range / (average + 1e-3)
            skewness = (average - median) / (price_range + 1e-3)
            volatility = (max_price / (min_price + 1e-3)) if min_price > 0 else 1.0

            # 📏 Unit-based normalization factor (based on real-world scale)
            unit_factor = 1.0
            if "50" in unit and "kg" in unit:
                unit_factor = 0.05
            elif "kg" in unit:
                unit_factor = 0.001
            elif "m3" in unit or "m²" in unit or "m2" in unit:
                unit_factor = 1.0
            elif "ton" in unit:
                unit_factor = 1.0
            elif "piece" in unit or "grain" in unit:
                unit_factor = 1.0
            elif "meter" in unit or unit == "m":
                unit_factor = 1.0

            # 🎯 Current price estimation using weighted components
            base_price = (0.2 * min_price) + (0.3 * median) + (0.4 * average) + (0.1 * max_price)

            # 🎯 Apply unit factor & cap at max_price
            current_price = min(base_price * unit_factor, max_price)

            # Add to training set
            X.append([
                min_price, max_price, average, median,
                price_range, mid_diff,
                range_ratio, skewness, volatility
            ])
            y.append(current_price)

# ✅ Convert data
X = np.array(X)
y = np.array(y)

# ✅ Train with polynomial regression + regularization
model = make_pipeline(PolynomialFeatures(degree=2, include_bias=False), Ridge(alpha=0.7))
model.fit(X, y)

# ✅ Save the model
os.makedirs("models", exist_ok=True)
with open("models/ai_price_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Final model trained with price heuristics, unit normalization, and saved to models/ai_price_model.pkl")
