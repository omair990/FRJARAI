import re

def clean_product_name(name):
    name = name.lower()
    # Remove brand names, noise words
    name = re.sub(r"\b(sabic|saudi|national|united|group|company|co\.?)\b", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name
