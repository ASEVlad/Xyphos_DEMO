import time
import threading
from loguru import logger
from telegram import Bot

from src.messages import *
from src.prompts import generate_creature_stats_prompt, generate_battle_content
from src.gpt_helper.llm_helper import generate_creature_appearance, fetch_ai_response, \
    generate_simple_content
from src.utils import get_creature_appearance_path, set_stats, set_creature_param, \
    get_random_opponent_chat_id, get_random_arena, parse_stats, extract_creature_features, parse_battle_text, \
    save_battle_records_to_csv


def handle_operation(bot: Bot, chat_id: str, message_text: str):
    logger.info(f"Chat_id {chat_id}: Received message: {message_text}")
    if message_text.lower().startswith("/mint"):
        handle_mint_action(bot, chat_id, message_text)
    elif message_text.lower().startswith("/name"):
        handle_name_action(bot, chat_id, message_text)
    elif message_text.lower().startswith("/stats"):
        handle_stats_action(bot, chat_id)
    elif message_text.lower().startswith("/training"):
        handle_training_action(bot, chat_id, message_text)
    elif message_text.lower().startswith("/pvp"):
        handle_pvp_action(bot, chat_id)
    elif message_text.lower().startswith("/contacts"):
        handle_contacts_action(bot, chat_id)
    elif message_text.lower().startswith("/executive_summary"):
        handle_executive_summary_action(bot, chat_id)
    else:
        bot.send_message(chat_id=chat_id, text=wrong_command_message)
    logger.info(f"Chat_id {chat_id}: Operation was successfully processed")


# MINT
def handle_mint_action(bot: Bot, chat_id: str, message_text: str):
    try:
        logger.info(f"Chat_id {chat_id}: Starting mint action")
        photo_ready_event = threading.Event()
        threading.Thread(target=run_creature_generation, args=(bot, chat_id, message_text, photo_ready_event)).start()
        time.sleep(15)
        bot.send_message(chat_id=chat_id, text=proper_mint_message_2)
        time.sleep(15)
        bot.send_message(chat_id=chat_id, text=proper_mint_message_3)
        photo_ready_event.set()
        logger.info(f"Chat_id {chat_id}: Finished mint action")

    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


def run_creature_generation(bot: Bot, chat_id: str, message_text: str, photo_ready_event):
    try:
        logger.info(f"Chat_id {chat_id}: Starting creature appearance generation")
        creature_description = message_text[5:].strip()
        if len(creature_description) == 0:
            creature_description = "Fairy from the hell with head of medusa from Greek mythology"
            bot.send_message(chat_id=chat_id, text=empty_mint_message)
        else:
            bot.send_message(chat_id=chat_id, text=proper_mint_message_1)

        set_creature_param(chat_id, "user_description", creature_description)
        abs_character_appearance_path = generate_creature_appearance(chat_id)

        # Wait until handle_operation signals "after message 3"
        photo_ready_event.wait()
        with open(abs_character_appearance_path, "rb") as photo:
            bot.send_photo(chat_id=chat_id, photo=photo, caption=generated_character_message)

        logger.info(f"Chat_id {chat_id}: Creature appearance generation complete")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# NAME
def handle_name_action(bot: Bot, chat_id: str, message_text: str):
    try:
        logger.info(f"Chat_id {chat_id}: Starting name action")
        if message_text.strip() == "/name":
            bot.send_message(chat_id=chat_id, text=empty_name_message)
        else:
            creature_name = message_text[5:].strip()
            set_creature_param(chat_id, "name", creature_name)
            bot.send_message(chat_id=chat_id, text=proper_name_message)

        logger.info(f"Chat_id {chat_id}: Name action complete")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# STATS
def handle_stats_action(bot: Bot, chat_id: str):
    try:
        logger.info(f"Chat_id {chat_id}: Starting stats action")
        bot.send_message(chat_id=chat_id, text=stats_message)

        creature_appearance_path = get_creature_appearance_path(chat_id)
        content_message = generate_creature_stats_prompt(chat_id)
        prompt_content = generate_simple_content(content_message, creature_appearance_path)

        creature_stats_response = fetch_ai_response(prompt_content)
        set_creature_param(chat_id, "stat_description", creature_stats_response)

        stats_parsed = parse_stats(creature_stats_response)
        set_stats(chat_id, stats_parsed)

        creature_features = extract_creature_features(creature_stats_response)
        set_creature_param(chat_id, "features", creature_features)

        finish_creature_mint_message = generate_finish_creature_mint_message_1(chat_id)
        bot.send_message(chat_id=chat_id, text=finish_creature_mint_message)
        time.sleep(1)

        random_opponent_creature_appearance_path = get_creature_appearance_path(chat_id)
        with open(random_opponent_creature_appearance_path, "rb") as photo:
            bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=generate_finish_creature_mint_message_2(chat_id)
            )
        time.sleep(1)

        finish_creature_mint_message = generate_finish_creature_mint_message_3(chat_id)
        bot.send_message(chat_id=chat_id, text=finish_creature_mint_message)

        time.sleep(20)

        bot.send_message(chat_id=chat_id, text=try_pvp_message)

        logger.info(f"Chat_id {chat_id}: Stats action complete")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


def handle_training_action(bot, chat_id, message_text):
    pass


# PVP
def handle_pvp_action(bot, first_player_chat_id):
    try:
        logger.info(f"Chat_id {first_player_chat_id}: Starting PVP action")
        bot.send_message(chat_id=first_player_chat_id, text=pvp_start_message)
        time.sleep(2)

        arena_name, arena_image_path, arena_description, arena_lore = get_random_arena()
        with open(arena_image_path, "rb") as photo:
            bot.send_photo(
                chat_id=first_player_chat_id,
                photo=photo,
                caption=generate_arena_announcement_message(arena_name, arena_lore)
            )
        time.sleep(10)

        random_opponent_chat_id = get_random_opponent_chat_id(first_player_chat_id)
        random_opponent_creature_appearance_path = get_creature_appearance_path(random_opponent_chat_id)
        with open(random_opponent_creature_appearance_path, "rb") as photo:
            bot.send_photo(
                chat_id=first_player_chat_id,
                photo=photo,
                caption=generate_opponent_announcement_message_1(random_opponent_chat_id)
            )
            time.sleep(3)
        bot.send_message(chat_id=first_player_chat_id, text=generate_opponent_announcement_message_2(random_opponent_chat_id))

        content = generate_battle_content(
            arena_image_path,
            arena_description,
            first_player_chat_id,
            random_opponent_chat_id
        )

        fight_info = fetch_ai_response(content)
        parsed_fight_info = parse_battle_text(fight_info)

        save_battle_records_to_csv(parsed_fight_info, first_player_chat_id, random_opponent_chat_id)
        bot.send_message(chat_id=first_player_chat_id, text=generate_battle_message(parsed_fight_info))

        time.sleep(20)

        bot.send_message(chat_id=first_player_chat_id, text=generate_battle_message(parsed_fight_info))
        logger.info(f"Chat_id {first_player_chat_id}: PVP action complete")
    except Exception as error:
        logger.error(f"Chat_ID {first_player_chat_id}: {error}")
        bot.send_message(chat_id=first_player_chat_id, text=error_message)


# CONTACTS
def handle_contacts_action(bot: Bot, chat_id: str):
    bot.send_message(chat_id=chat_id, text=contact_message)


# EXECUTIVE SUMMARY
def handle_executive_summary_action(bot, chat_id):
    bot.send_message(chat_id=chat_id, text=executive_summary_message)