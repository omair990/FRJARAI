import pandas as pd

def smart_clean_building_data(df):
    df_cleaned = pd.DataFrame(df).drop_duplicates(subset=["Product Name", "Unit"], keep="first")

    def flag_price_collision(row):
        name = row["Product Name"]
        unit = row["Unit"]
        avg_price = row["Current Average Price (SAR)"]

        if "مم" in name:
            size = ''.join(filter(str.isdigit, name))
            base_name = name.replace(size + "مم", "").strip()

            matches = df_cleaned[
                (df_cleaned["Product Name"].str.contains(base_name)) &
                (df_cleaned["Unit"] == unit) &
                (df_cleaned["Product Name"] != name)
            ]

            for _, match in matches.iterrows():
                other_price = match["Current Average Price (SAR)"]
                if abs(avg_price - other_price) < 0.05:
                    return "⚠️ Possible Price Overlap"
        return ""

    df_cleaned["Notes"] = df_cleaned.apply(flag_price_collision, axis=1)

    aluminum_index = df_cleaned[df_cleaned["Product Name"].str.contains("ألمنيوم")].index
    if not aluminum_index.empty:
        df_cleaned.loc[aluminum_index, "Notes"] = "ℹ️ Confirm per-ton to meter/piece conversion"

    return df_cleaned
