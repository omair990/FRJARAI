# utils/feature_extractor.py

def extract_features(product):
    min_price = product.get("min_price") or 0.0
    max_price = product.get("max_price") or 0.0
    average = product.get("average") or 0.0
    median = product.get("median") or 0.0
    unit = product.get("unit", "").lower()

    price_range = max_price - min_price
    mid_diff = average - median
    range_ratio = price_range / (average + 1e-3)
    skewness = (average - median) / (price_range + 1e-3)
    volatility = (max_price / (min_price + 1e-3)) if min_price > 0 else 1.0
    symmetry_index = abs((average - median) / (average + 1e-3))
    price_centering = (median - min_price) / (price_range + 1e-3)
    price_spread_factor = (max_price - average) / (price_range + 1e-3)

    return [
        min_price, max_price, average, median,
        price_range, mid_diff,
        range_ratio, skewness, volatility,
        symmetry_index, price_centering, price_spread_factor
    ]
