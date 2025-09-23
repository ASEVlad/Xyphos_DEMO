import os

import pandas as pd

from src.utils import get_creature_param

welcome_message = (
    "Welcome to Xyphos! Step into a world where creatures evolve, battle, and forge their own legends."
    "\nFrom here, you have a few paths to choose from."
    "\nYou can explore the wide range of actions available—including checking our contacts and executive summary."
    "\nBut we recommend starting by creating your very first creature."
    "\nSimply type /mint and describe how your creature should look."
)

repeated_login = "You are already registered. Thank you for testing us."

empty_mint_message = (
    "\nOh... it looks like you clicked /mint without adding a description, or maybe you just ran out of time."
    "\nDon’t worry! If you’d like to create another creature, simply follow the guide from the previous message."
    "\nFor now, we’re already crafting a creature for you!"
    "\nThe description we’re using comes from the example above:"
    "\n"
    "\nFairy from the hell with the head of Medusa from Greek mythology"
    "\n"
    "\nWhile you wait, why not think of a fitting name for this creature?"
)


proper_mint_message_1 = (
    "\nAmazing! You are on your way for creating your own creature."
    "\nWe are already creating the creature for you!"
    "\nAnd while you wait, why not think of a fitting name for this creature?"
)

proper_mint_message_2 = (
    "\nHere are a few things to know about the creature you’re bringing to life."
    "\nEach one has its own Rarity, Level, and the potential for Evolution."
    "\nThere are six Rarities, from Common all the way up to Mythic."
    "\nThe rarer the creature, the greater the perks and advantages it will carry into battle."
    "\nYour creature can grow up to 50 Levels in total."
    "\nWith each Level, its stats rise—and new surprises unfold."
    "\nEvery 5 Levels, it unlocks a fresh skill that you get to shape."
    "\nAnd every 10 Levels, it Evolves—transforming into a stronger, grander form with an even more striking appearance."
)

proper_mint_message_3 = (
    "\nFrom the description that you have just provided, our algorithm breathes life into your creature, shaping a set of truly unique stats."
    "\nSome will feel familiar — like HP, strength, or magical attack."
    "\nBut others may surprise you, with rare traits that shift with every choice you make — Mood, or Fatigue that rises and falls with Training, Fighting, or even simple Conversations."
    "\nThere’s even Attachment — the bond your creature feels toward you — which can grow stronger with care and visits, or weaken with neglect and the tone of your words."
    "\nSo treat your creature not just as a character, but as a living being. Because in more ways than one... they are."
)

generated_character_message = (
    "\nWooow. It looks stunning. And a bit cute... 😊"
    "\nNow you can name it."
    "\nFor this please type /name and write the name that you want to give to your creature."
    "\nExample:"
    "\n/name Evil_Fairy"
)

proper_name_message = (
    "\nWhat a wonderful name! If only everyone had such creativity."
    "\nYour creature is nearly complete — the only thing left are its stats."
    "\nTo begin forging them, just click /stats and we’ll start shaping your creature’s power."
)

empty_name_message = (
    "\nOh no... your creature doesn’t have a name yet!"
    "\nPlease send us /name followed by the name you’d like to give it, and we’ll move on to the final step."
    "\nExample:"
    "\n/name Evil_Fairy"
).strip()

stats_message = (
    "\nAmazing!"
    "\nWe are already forging stats for your creature, and in just a few moments your new companion will be ready to step into the beautiful world of Xyphos."
)

def generate_finish_creature_mint_message_1(chat_id: str):
    message =  (
        "\nAnd here we are..."
        "\nHere is your brand new creature"
    )
    return message

def generate_finish_creature_mint_message_2(chat_id: str):
    creature_name = get_creature_param(chat_id, "name")
    message =  (
        f"\n\n{creature_name.upper()}"
    )
    return message

def generate_finish_creature_mint_message_3(chat_id: str):
    creature_stats = get_creature_param(chat_id, "stat_description")

    message =  (
        "\n\nAnd here are your creature stats with its own features:"
        f"\n{creature_stats}"
    )
    return message

try_pvp_message = (
    "\nHappy with the creature you’ve created? We bet you are! :)"
    "\nNow it’s time to test their strength in the field!"
    "\nJust type /pvp and we’ll find an arena with a worthy opponent for you."
)

pvp_start_message = (
    "\nGreat!"
    "\nLets try to test you creature in a real fight!"
)

def generate_arena_announcement_message(arena_name, arena_lore, campaign_mode=False):
    if campaign_mode:
        message = f"You have got into {arena_name.upper()}"
    else:
        message = (
            "\nAn empty arena has been found for you!"
            f"\n"
            f"\n{arena_name.upper()}"
        )

    message += (
        "\n"
        f"\n{arena_lore}"
    )
    return message

def generate_opponent_announcement_message_1(opponent_player_creature_name):
    message = (
        f"\nYour Opponent:"
        f"\n"
        f"\n{opponent_player_creature_name}"
    )

    return message

def generate_opponent_announcement_message_2(opponent_player_creature_description):
    message = (
        f"\nStats:"
        f"\n{opponent_player_creature_description}"
    )

    return message

def generate_battle_message(parsed_fight_info):
    message = (
        f"\n{parsed_fight_info['Story']}"
        f"\n"
        f"\n"
        f"\nMechanics:"
        f"\n{parsed_fight_info['Mechanics']}"
        f"\n"
        f"\n --------"
        f"\n"
    )

    if parsed_fight_info["Winner"].lower() == "player 1":
        message += "🎉🎉🎉\nYOU ARE THE WINNER!\nCONGRATZZZ\n🎉🎉🎉"
    else:
        message += "\nYou were defeated...\nMaybe try once more?\n"

    return message

try_training_message = (
    "Did you enjoy the PvP battle? Exciting, wasn’t it?"
    "\nNow, how about trying a training session?"
    "\nJust type /training followed by your preferred activity for the next 30 minutes."
    "\nRemember: the more thoughtful, polite, and enjoyable your training description is, the greater the benefits your creature will gain."
    "\nExample:"
    "\n/training Let's practice dodging both melee and ranged attacks for 30 minutes in a fun, game-like style."
)

empty_training_message = (
    "Ohh... no... You have not provided the training text."
    "\nBut don’t worry! WE will use an Example for you"
    "\nBut if you want to train the creature once more - type /training followed by your preferred activity for the next 30 minutes."
    "\nExample:"
    "\n/training Let's practice dodging both melee and ranged attacks for 30 minutes in a fun, game-like style."
)

wrong_command_message = "We are sorry to mislead you... Please try again. Operation was not detected"

error_message = "Oh... no... Something happened from our side. Please try the last operation one more time. Or if you are totally lost type /info"

ai_error_message = "Oh... no... Something happened from AI side. Please try the last operation one more time."


def generate_stats_difference_message(old_stats: dict, new_stats: dict) -> str:
    messages = ["Cool! Your creature is upgrading!\n\n📊 Stats have been changed:"]

    for stat, old_val in old_stats.items():
        if stat in new_stats:
            new_val = new_stats[stat]
            if new_val != old_val:
                diff = new_val - old_val
                sign = "↑" if diff > 0 else "↓"
                messages.append(
                    f"- {stat}: {old_val} → {new_val} ({sign}{abs(diff)})"
                )

    # Check if new stats introduced something fresh
    for stat, new_val in new_stats.items():
        if stat not in old_stats:
            messages.append(f"- {stat}: NEW → {new_val}")

    if len(messages) == 1:
        return "✅ No stat changes."

    return "\n".join(messages)

def generate_new_features_message(feature: str) -> str:
    message = (
        "We took the liberty of imagining you carried out similar training five more times..."
        "\nAnd that’s how you unlocked a BRAND NEW FEATURE!"
        "\nKeep in mind, it’s not as powerful as the skills you’ll gain at Level 5,"
        "\nbut it still adds unique flavor to your creature."
        f"\nYour new feature is: "
        f"\n{feature}"
    )
    return message


finish_training_message = (
    "That was impressive journey."
    "\nBut that's not the end!"
    "\nThere are immerse other options. Few of them are:"
    "\n1. Campaign Mode where you can find few different NPC creatures to fight with. For trying your creature in new mode just press /campaign"
    "\n2. Get contacts of the founder. For this simply press /contacts"
    "\n3. Get executive summary. And this is as simple as the previous ones. Just type /executive_summary"
    "\n"
    "\nNow. It is your turn to choose destiny for your creature"
)

general_info_message = (
    "\n1. Generate new creature - type /mint and description, then /name the name of it, after type /stats."
    "\n2. Play against other people creatures - just press /pvp"
    "\n3. Campaign Mode with more levels - just press /campaign"
    "\n4. Train your creature - type /training and the orders text"
    "\n5. Get contacts of the founder - type /contacts"
    "\n6. Get executive summary - type /executive_summary"
)

info_message = (
    f"Here are all the options that we have for now"
    f"{general_info_message}"
)

finish_campaign_message = (
    "That is the end!"
    "\nIf you want to play a bit more - then you are more then welcome. Here are your options:"
    f"{general_info_message}"
    "\n"
    "\nGood Luck anf Have Fun!"
)

contacts_message = (
    "Contacts are more important than ever in our time."
    "\nWe’re glad you understand that!"
    "\nHere’s our Linktree, where you can find all the links you might need:"
    "\nhttps://linktr.ee/asevlad"
)

executive_summary_message = (
    "Mmm... we see your determination."
    "\nAnd we truly appreciate it!"
    "\nThat’s why we’re sharing access to our Executive Summary:"
    "\nhttps://drive.google.com/file/d/13liPJ5_kwbU2PwcPZ3daUqLVeMBwPuIO/view?usp=sharing"
)

def generate_check_message():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CREATURE_DB_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "creature_db.csv"))
    BATTLE_RECORDS_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "battle_records.csv"))
    USER_STATUS_DB = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "user_status.csv"))

    creature_records_df = pd.read_csv(CREATURE_DB_FILE)
    battle_records_df = pd.read_csv(BATTLE_RECORDS_FILE)
    user_status_df = pd.read_csv(USER_STATUS_DB)
    user_in_progress_df = user_status_df[user_status_df['status'] == 'In Progress']

    messages = (
        f"There are {len(creature_records_df)} creatures."
        f"\nThere are {len(battle_records_df)} battles."
        f"\nThere are {len(user_in_progress_df)} users with status 'In Progress'."
    )
    return messages