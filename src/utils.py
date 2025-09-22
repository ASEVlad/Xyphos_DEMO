import base64
import os
import re
import time
from datetime import datetime

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREATURE_APPEARANCE_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "creature_appearances"))
CREATURE_DB_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "creature_db.csv"))
ARENA_DB_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "arenas", "arena_db.csv"))
BATTLE_RECORDS_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "battle_records.csv"))
USER_STATUS_DB = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "user_status.csv"))
CAMPAIGN_CREATURE_DB = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "campaign_creature_db.csv"))


def get_creature_appearance_path(chat_id: str) -> str:
    creature_stats_appearance_path = os.path.join(CREATURE_APPEARANCE_FOLDER, f"{chat_id}.png")

    return creature_stats_appearance_path


def set_creature_param(chat_id: str, param: str, value):
    # Ensure file exists
    if not os.path.exists(CREATURE_DB_FILE):
        df = pd.DataFrame(columns=["chat_id"])
        df.to_csv(CREATURE_DB_FILE, index=False)

    # Load
    df = pd.read_csv(CREATURE_DB_FILE)

    # If param column doesn't exist → create it with NaN
    if param not in df.columns:
        df[param] = pd.NA

    # If chat_id exists → update, else append
    if chat_id in df["chat_id"].astype(str).values:
        df.loc[df["chat_id"].astype(str) == chat_id, param] = value
        is_new = False
    else:
        # Create row with all columns NaN, then fill param
        new_row = {col: pd.NA for col in df.columns}
        new_row["chat_id"] = chat_id
        new_row[param] = value
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        is_new = True

    # Save back
    df.to_csv(CREATURE_DB_FILE, index=False)
    return is_new


def get_creature_param(chat_id: str, param: str) -> str | None:
    if not os.path.exists(CREATURE_DB_FILE):
        return None

    df = pd.read_csv(CREATURE_DB_FILE)
    match = df.loc[df["chat_id"].astype(str) == str(chat_id), param]

    if not match.empty:
        return match.iloc[0]
    return None


# Canonical keys we care about
CANON_KEYS = [
    'Health Points', 'Attack', 'Defense', 'Agility', 'Magic Attack', 'Magic Defense',
    'Mood', 'Fatigue', 'Attachment to Owner', 'Obedience', 'Experience', 'Level'
]

STAT_REGEX = r'(?P<name>[\w\s]+?)\s*(?:\((?P<abbr>\w+)\))?\s*:\s*(?P<value>\d+)\s*(?:\((?P<range>[^)]+)\))?'
STAT_DELIMITER = "\n\n"  # Assuming stats are on separate lines

def parse_stats(input_text):
    # Split input into lines and process each
    lines = input_text.strip().split(STAT_DELIMITER)
    stats_for_chat = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        match = re.match(STAT_REGEX, line)
        if match:
            name = match.group('name').strip()
            value = int(match.group('value'))

            # Store in a sub-dict for this stat
            stats_for_chat[name] = value
        # Else: Ignore non-matching lines (e.g., descriptions)

    # Map to chat_id in the dataset

    return stats_for_chat  # Or return the full DATASET if needed


def set_stats(chat_id: str, stats: dict) -> None:
    """
    Upsert a single row keyed by chat_id with provided stats.
    Missing stats remain as-is (no overwrite to NaN).
    """
    df = pd.read_csv(CREATURE_DB_FILE)

    if "chat_id" not in df.columns:
        # Repair if file got corrupted
        cols = ["chat_id"] + CANON_KEYS
        df = pd.DataFrame(columns=cols)

    # Make sure all canonical columns exist
    for c in CANON_KEYS:
        if c not in df.columns:
            df[c] = pd.NA
    if "updated_at" not in df.columns:
        df["updated_at"] = pd.NA

    if chat_id in df["chat_id"].astype(str).values:
        idx = df.index[df["chat_id"].astype(str) == str(chat_id)][0]
        for k, v in stats.items():
            df.at[idx, k] = v
    else:
        row = {"chat_id": chat_id}
        for k in CANON_KEYS:
            row[k] = stats.get(k, pd.NA)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df.to_csv(CREATURE_DB_FILE, index=False)


def get_stats(chat_id: str) -> dict | None:
    """
    Return stats dict for chat_id or None if not found.
    """
    df = pd.read_csv(CREATURE_DB_FILE)
    if "chat_id" not in df.columns:
        return None
    mask = df["chat_id"].astype(str) == str(chat_id)
    if not mask.any():
        return None
    row = df.loc[mask].iloc[0].to_dict()
    # Strip metadata
    row.pop("updated_at", None)
    # Return only canonical keys + chat_id
    return {"chat_id": row.get("chat_id")} | {k: row.get(k) for k in CANON_KEYS}


def extract_creature_features(text: str):
    # Step 1: find Creature Features block
    match = re.search(r"Creature Features\s+(.*)", text, re.S)
    if not match:
        return {}

    return match.group(1).strip()


def get_random_opponent_chat_id(player_chat_id: str) -> str:
    df = pd.read_csv(CREATURE_DB_FILE)
    opponent_chat_id = df[df["chat_id"].astype("str") != str(player_chat_id)]["chat_id"].sample().iloc[0]
    return opponent_chat_id

def get_random_arena():
    df = pd.read_csv(ARENA_DB_FILE)
    random_arena = df.sample().iloc[0]
    random_arena_name = random_arena["name"]
    random_arena_image_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "arenas", "images", f"{random_arena_name}.png"))
    random_arena_description = random_arena["description"]
    random_arena_lore = random_arena["lore_message"]

    return random_arena_name, random_arena_image_path, random_arena_description, random_arena_lore

def get_campaign_arena():
    df = pd.read_csv(ARENA_DB_FILE)
    random_arena = df[df["name"] == "Forest Clearing"].iloc[0]
    random_arena_name = random_arena["name"]
    random_arena_image_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "arenas", "images", f"{random_arena_name}.png"))
    random_arena_description = random_arena["description"]
    random_arena_lore = random_arena["lore_message"]

    return random_arena_name, random_arena_image_path, random_arena_description, random_arena_lore


def get_image_in_b64_format(image_path: str):
    with open(image_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")
    return b64_img


def parse_battle_text(text):
    # Define regex patterns for each section
    story_pattern = r'^Story:\s*\n(.*?)(\n\nMechanics:|\Z)'
    mechanics_pattern = r'^Mechanics:\s*\n(.*?)(\n\nWinner:|\Z)'
    winner_pattern = r'^Winner:\s*\n(.*?)(\Z|\n\n)'

    # Extract Story
    story_match = re.search(story_pattern, text, re.MULTILINE | re.DOTALL)
    story = story_match.group(1).strip() if story_match else ""

    # Extract Mechanics
    mechanics_match = re.search(mechanics_pattern, text, re.MULTILINE | re.DOTALL)
    mechanics = mechanics_match.group(1).strip() if mechanics_match else ""

    # Extract Winner
    winner_match = re.search(winner_pattern, text, re.MULTILINE | re.DOTALL)
    winner = winner_match.group(1).strip() if winner_match else ""

    return {
        "Story": story,
        "Mechanics": mechanics,
        "Winner": winner
    }


def save_battle_records_to_csv(fight_info, data, first_chat_id, second_chat_id):
    # Define headers
    headers = ['ID', 'Timestamp', 'First_Chat_ID', 'Second_Chat_ID', 'Full text', 'Story', 'Mechanics', 'Winner']

    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Load existing CSV or create new DataFrame
    if os.path.exists(BATTLE_RECORDS_FILE):
        df = pd.read_csv(BATTLE_RECORDS_FILE)
        next_id = df['ID'].max() + 1 if not df.empty else 1
    else:
        df = pd.DataFrame(columns=headers)
        next_id = 1

    # Create new record
    new_record = {
        'ID': next_id,
        'Timestamp': timestamp,
        'First_Chat_ID': first_chat_id,
        'Second_Chat_ID': second_chat_id,
        'Full text': fight_info,
        'Story': data['Story'],
        'Mechanics': data['Mechanics'],
        'Winner': data['Winner']
    }

    # Append new record
    new_df = pd.DataFrame([new_record])
    df = pd.concat([df, new_df], ignore_index=True)

    # Save to CSV
    df.to_csv(BATTLE_RECORDS_FILE, index=False, encoding='utf-8')

    return next_id


NEW_STAT_REGEX = r'(?P<name>[\w\s]+?)\s*(?:\((?P<abbr>\w+)\))?\s*:\s*(?P<value>[0-9.]+)'
FEATURE_REGEX = r'New feature:\s*(?P<feature>.+)'


def parse_stats_and_feature(input_text: str) -> tuple[dict, str]:
    """
    Parse stats and feature from input text.
    Returns a tuple of (stats dictionary, feature string).
    """
    stats = {}
    feature = None

    # Split into sections
    sections = input_text.strip().split('\n\n')

    for section in sections:
        section = section.strip()
        if section.startswith('Stat changes:'):
            # Process stat lines
            stat_lines = section.split('\n')[1:]  # Skip "Stat changes:" line
            for line in stat_lines:
                line = line.strip()
                if not line:
                    continue
                match = re.match(NEW_STAT_REGEX, line)
                if match:
                    name = match.group('name').strip()
                    try:
                        value = float(match.group('value'))
                        # Convert to int if it's a whole number
                        if value.is_integer():
                            value = int(value)
                        stats[name] = value
                    except ValueError:
                        continue  # Skip invalid numeric values
        elif section.startswith('New feature:'):
            # Process feature line
            match = re.match(FEATURE_REGEX, section)
            if match:
                feature = match.group('feature').strip()

    return stats, feature


def update_stats_and_feature(chat_id: str, stats: dict, feature: str) -> None:
    """
    Parse stats and feature from input text and upsert into the database.
    Missing stats remain as-is (no overwrite to NaN).
    """
    # Read or initialize the database
    try:
        df = pd.read_csv(CREATURE_DB_FILE)
    except FileNotFoundError:
        cols = ["chat_id"] + CANON_KEYS + ["Feature", "updated_at"]
        df = pd.DataFrame(columns=cols)

    # Ensure all necessary columns exist
    for c in CANON_KEYS + ["Feature", "updated_at"]:
        if c not in df.columns:
            df[c] = pd.NA

    # Update or insert the row
    current_time = datetime.now().isoformat()
    if chat_id in df["chat_id"].astype(str).values:
        idx = df.index[df["chat_id"].astype(str) == str(chat_id)][0]
        # Update existing stats
        for k, v in stats.items():
            if k in CANON_KEYS:
                df.at[idx, k] = v
        # Update feature if present
        if feature:
            df.at[idx, "Feature"] += "\n" + feature
        df.at[idx, "updated_at"] = current_time
    else:
        # Create new row
        row = {"chat_id": chat_id, "updated_at": current_time}
        for k in CANON_KEYS:
            row[k] = stats.get(k, pd.NA)
        row["Feature"] = feature if feature else pd.NA
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Save to database
    df.to_csv(CREATURE_DB_FILE, index=False)


def set_user_status(chat_id: str, param: str, value):
    # Ensure file exists
    if not os.path.exists(USER_STATUS_DB):
        df = pd.DataFrame(columns=["chat_id", "status", "updated_at"])
        df.to_csv(USER_STATUS_DB, index=False)

    # Load
    df = pd.read_csv(USER_STATUS_DB)

    # If param column doesn't exist → create it with NaN
    if param not in df.columns:
        df[param] = pd.NA

    # If chat_id exists → update, else append
    if chat_id in df["chat_id"].astype(str).values:
        df.loc[df["chat_id"].astype(str) == chat_id, param] = value
        is_new = False
    else:
        # Create row with all columns NaN, then fill param
        new_row = {col: pd.NA for col in df.columns}
        new_row["chat_id"] = chat_id
        new_row[param] = value
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        is_new = True

    # Save back
    df.to_csv(USER_STATUS_DB, index=False)
    return is_new


def get_user_status(chat_id: str, param: str) -> str | None:
    if not os.path.exists(USER_STATUS_DB):
        return None

    df = pd.read_csv(USER_STATUS_DB)
    match = df.loc[df["chat_id"].astype(str) == str(chat_id), param]

    if not match.empty:
        return match.iloc[0]
    return None


def wait_till_proper_user_status(chat_id):
    while get_user_status(chat_id, "status") != "In Progress":
        time.sleep(1)


def get_campaign_creature_param(chat_id: str, param: str) -> str | None:
    if not os.path.exists(CAMPAIGN_CREATURE_DB):
        return None

    df = pd.read_csv(CAMPAIGN_CREATURE_DB)
    match = df.loc[df["chat_id"].astype(str) == str(chat_id), param]

    if not match.empty:
        return match.iloc[0]
    return None