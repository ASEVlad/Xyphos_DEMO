import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREATURE_DB_FILE = os.path.abspath(os.path.join(BASE_DIR, "data", "creature_db.csv"))

def ensure_creature_columns():
    # Ensure file exists
    if not os.path.exists(CREATURE_DB_FILE):
        # Create an empty DataFrame with at least these columns
        df = pd.DataFrame(columns=["chat_id", "Campaign_level"])
    else:
        df = pd.read_csv(CREATURE_DB_FILE)

        # Add missing columns with default value 0
        for col in ["Campaign_level"]:
            if col not in df.columns:
                df[col] = 0

    # Save back
    df.to_csv(CREATURE_DB_FILE, index=False)
    return df

# Example usage:
if __name__ == "__main__":
    creature_df = ensure_creature_columns()
    print(creature_df.head())