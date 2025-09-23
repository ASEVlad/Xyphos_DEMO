import time
import threading
from loguru import logger
from telegram import Bot

from src.messages import *
from src.prompts import generate_creature_stats_prompt, generate_battle_content, generate_training_prompt
from src.gpt_helper.llm_helper import generate_creature_appearance, fetch_ai_response, \
    generate_simple_content
from src.utils import get_creature_appearance_path, set_stats, set_creature_param, \
    get_random_opponent_chat_id, get_random_arena, parse_stats, extract_creature_features, parse_battle_text, \
    save_battle_records_to_csv, parse_stats_and_feature, update_stats_and_feature, get_stats, \
    wait_till_proper_user_status, set_user_status, get_campaign_arena, get_campaign_creature_param, reset_user


def handle_operation(bot: Bot, chat_id: str, message_text: str):
    logger.info(f"Chat_id {chat_id}: Received message: {message_text}")
    if message_text.lower().startswith("/mint"):
        threading.Thread(target=handle_mint_action, args=(bot, chat_id, message_text)).start()
    elif message_text.lower().startswith("/name"):
        threading.Thread(target=handle_name_action, args=(bot, chat_id, message_text)).start()
    elif message_text.lower().startswith("/stats"):
        threading.Thread(target=handle_stats_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/training"):
        threading.Thread(target=handle_training_action, args=(bot, chat_id, message_text)).start()
    elif message_text.lower().startswith("/pvp"):
        threading.Thread(target=handle_pvp_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/contacts"):
        threading.Thread(target=handle_contacts_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/executive_summary"):
        threading.Thread(target=handle_executive_summary_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/info"):
        threading.Thread(target=handle_info_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/check"):
        threading.Thread(target=handle_check_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/campaign"):
        threading.Thread(target=handle_campaign_action, args=(bot, chat_id)).start()
    elif message_text.lower().startswith("/reset_user"):
        threading.Thread(target=handle_reset_user_action, args=(bot, chat_id, message_text)).start()
    else:
        bot.send_message(chat_id=chat_id, text=wrong_command_message)
    logger.info(f"Chat_id {chat_id}: Operation was successfully processed")


# MINT
def handle_mint_action(bot: Bot, chat_id: str, message_text: str):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting mint action")
        photo_ready_event = threading.Event()
        threading.Thread(target=run_creature_generation, args=(bot, chat_id, message_text, photo_ready_event)).start()

        set_creature_param(chat_id, "Experience", 0)
        set_creature_param(chat_id, "Campaign_level", 0)
        set_creature_param(chat_id, "Training_count", 0)

        time.sleep(15)
        bot.send_message(chat_id=chat_id, text=proper_mint_message_2)
        time.sleep(15)
        bot.send_message(chat_id=chat_id, text=proper_mint_message_3)
        photo_ready_event.set()
        logger.info(f"Chat_id {chat_id}: Finished mint action")
        set_user_status(chat_id, "status", "Ready")

    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


def run_creature_generation(bot: Bot, chat_id: str, message_text: str, photo_ready_event):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting creature appearance generation")
        creature_description = message_text[5:].strip()
        if len(creature_description) == 0:
            creature_description = "Fairy from the hell with head of medusa from Greek mythology"
            bot.send_message(chat_id=chat_id, text=empty_mint_message)
        else:
            bot.send_message(chat_id=chat_id, text=proper_mint_message_1)

        set_creature_param(chat_id, "user_description", creature_description)
        abs_character_appearance_path = generate_creature_appearance(chat_id, creature_description)

        # Wait until handle_operation signals "after message 3"
        photo_ready_event.wait()
        with open(abs_character_appearance_path, "rb") as photo:
            bot.send_photo(chat_id=chat_id, photo=photo, caption=generated_character_message)

        logger.info(f"Chat_id {chat_id}: Creature appearance generation complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# NAME
def handle_name_action(bot: Bot, chat_id: str, message_text: str):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting name action")
        if message_text.strip() == "/name":
            bot.send_message(chat_id=chat_id, text=empty_name_message)
        else:
            creature_name = message_text[5:].strip()
            set_creature_param(chat_id, "name", creature_name)
            bot.send_message(chat_id=chat_id, text=proper_name_message)

        logger.info(f"Chat_id {chat_id}: Name action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# STATS
def handle_stats_action(bot: Bot, chat_id: str):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting stats action")
        bot.send_message(chat_id=chat_id, text=stats_message)

        creature_appearance_path = get_creature_appearance_path(chat_id)
        content_message = generate_creature_stats_prompt(chat_id)
        prompt_content = generate_simple_content(content_message, creature_appearance_path)

        creature_stats_response = fetch_ai_response(prompt_content)
        if len(creature_stats_response) <= 200:
            creature_stats_response = fetch_ai_response(prompt_content)
            if len(creature_stats_response) <= 200:
                creature_stats_response = fetch_ai_response(prompt_content)
                if len(creature_stats_response) <= 200:
                    creature_stats_response = fetch_ai_response(prompt_content)
                    if len(creature_stats_response) <= 200:
                        bot.send_message(chat_id=chat_id, text=ai_error_message)

        if len(creature_stats_response) <= 200:
            set_creature_param(chat_id, "stat_description", creature_stats_response)

            stats_parsed = parse_stats(creature_stats_response)
            set_stats(chat_id, stats_parsed)

            creature_features = extract_creature_features(creature_stats_response)
            set_creature_param(chat_id, "Feature", creature_features)

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
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


def handle_training_action(bot, chat_id, message_text):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting training action")
        if message_text.strip() == "/training":
            training_text = "Let's practice dodging both melee and ranged attacks for 30 minutes in a fun, game-like style."
            bot.send_message(chat_id=chat_id, text=empty_training_message)
        else:
            training_text = message_text[8:].strip()

        training_prompt = generate_training_prompt(chat_id, training_text)
        content = generate_simple_content(training_prompt, get_creature_appearance_path(chat_id))
        training_result_text = fetch_ai_response(content)
        new_stats, feature = parse_stats_and_feature(training_result_text)
        if not new_stats:
            training_result_text = fetch_ai_response(content)
            new_stats, feature = parse_stats_and_feature(training_result_text)
            if not new_stats:
                bot.send_message(chat_id=chat_id, text=ai_error_message)

        old_stats = get_stats(chat_id)
        update_stats_and_feature(chat_id, new_stats, feature)

        stats_difference_message = generate_stats_difference_message(old_stats, new_stats)
        bot.send_message(chat_id=chat_id, text=stats_difference_message)

        time.sleep(3)

        training_count = get_creature_param(chat_id, "Training_count")
        training_count += 1
        set_creature_param(chat_id, "Training_count", training_count)

        new_feature_message = generate_new_features_message(feature)
        bot.send_message(chat_id=chat_id, text=new_feature_message)

        time.sleep(5)

        bot.send_message(chat_id=chat_id, text=finish_training_message)

        logger.info(f"Chat_id {chat_id}: Training action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# PVP
def handle_pvp_action(bot, first_player_chat_id):
    try:
        set_user_status(first_player_chat_id, "status", "In Progress")
        wait_till_proper_user_status(first_player_chat_id)
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
        opponent_player_creature_name = get_creature_param(random_opponent_chat_id, "name")
        with open(random_opponent_creature_appearance_path, "rb") as photo:
            bot.send_photo(
                chat_id=first_player_chat_id,
                photo=photo,
                caption=generate_opponent_announcement_message_1(opponent_player_creature_name)
            )
            time.sleep(3)
        opponent_player_creature_description = get_creature_param(random_opponent_chat_id, "stat_description")
        bot.send_message(chat_id=first_player_chat_id, text=generate_opponent_announcement_message_2(opponent_player_creature_description))

        first_player_creature_name = get_creature_param(first_player_chat_id, "name")
        first_player_creature_description = get_creature_param(first_player_chat_id, "stat_description")
        first_player_creature_image_path = get_creature_appearance_path(first_player_chat_id)
        content = generate_battle_content(
            arena_image_path,
            arena_description,
            first_player_creature_name,
            first_player_creature_description,
            first_player_creature_image_path,
            opponent_player_creature_name,
            opponent_player_creature_description,
            random_opponent_creature_appearance_path
        )

        fight_info = fetch_ai_response(content)
        parsed_fight_info = parse_battle_text(fight_info)

        save_battle_records_to_csv(fight_info, parsed_fight_info, first_player_chat_id, random_opponent_chat_id)
        if len(parsed_fight_info["Story"]) != 0 and len(parsed_fight_info["Mechanics"]) != 0:
            bot.send_message(chat_id=first_player_chat_id, text=generate_battle_message(parsed_fight_info))
            logger.warning(f"Chat_id {first_player_chat_id}: Could not parse properly fight info")
        else:
            bot.send_message(chat_id=first_player_chat_id, text=fight_info)

        time.sleep(20)

        bot.send_message(chat_id=first_player_chat_id, text=try_training_message)

        logger.info(f"Chat_id {first_player_chat_id}: PVP action complete")
        set_user_status(first_player_chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {first_player_chat_id}: {error}")
        bot.send_message(chat_id=first_player_chat_id, text=error_message)


# CONTACTS
def handle_contacts_action(bot: Bot, chat_id: str):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting Contacts action")
        bot.send_message(chat_id=chat_id, text=contacts_message)
        logger.info(f"Chat_id {chat_id}: Contacts action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# EXECUTIVE SUMMARY
def handle_executive_summary_action(bot, chat_id):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting Executive Summary action")
        bot.send_message(chat_id=chat_id, text=executive_summary_message)
        logger.info(f"Chat_id {chat_id}: Executive Summary action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)

# INFO
def handle_info_action(bot, chat_id):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting PVP action")
        bot.send_message(chat_id=chat_id, text=info_message)
        logger.info(f"Chat_id {chat_id}: Info action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)

# CHECK
def handle_check_action(bot, chat_id):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting PVP action")
        check_message = generate_check_message()
        bot.send_message(chat_id=chat_id, text=check_message)
        logger.info(f"Chat_id {chat_id}: Info action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# NAME
def handle_campaign_action(bot: Bot, chat_id: str):
    try:
        set_user_status(chat_id, "status", "In Progress")
        wait_till_proper_user_status(chat_id)
        logger.info(f"Chat_id {chat_id}: Starting campaign action")

        arena_name, arena_image_path, arena_description, arena_lore = get_campaign_arena()
        with open(arena_image_path, "rb") as photo:
            bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=generate_arena_announcement_message(arena_name, arena_lore, campaign_mode=True)
            )
        time.sleep(10)

        campaign_level = int(get_creature_param(chat_id, "Campaign_level"))
        opponent_chat_id = f"Creature_{campaign_level + 1}"
        set_creature_param(chat_id, "Campaign_level", campaign_level+1)

        random_opponent_creature_appearance_path = get_creature_appearance_path(opponent_chat_id)
        opponent_player_creature_name = get_campaign_creature_param(opponent_chat_id, "name")
        with open(random_opponent_creature_appearance_path, "rb") as photo:
            bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=generate_opponent_announcement_message_1(opponent_player_creature_name)
            )
            time.sleep(3)
        opponent_player_creature_description = get_campaign_creature_param(opponent_chat_id, "stat_description")
        bot.send_message(chat_id=chat_id, text=generate_opponent_announcement_message_2(opponent_player_creature_description))

        first_player_creature_name = get_creature_param(chat_id, "name")
        first_player_creature_description = get_creature_param(chat_id, "stat_description")
        first_player_creature_image_path = get_creature_appearance_path(chat_id)
        content = generate_battle_content(
            arena_image_path,
            arena_description,
            first_player_creature_name,
            first_player_creature_description,
            first_player_creature_image_path,
            opponent_player_creature_name,
            opponent_player_creature_description,
            random_opponent_creature_appearance_path
        )

        fight_info = fetch_ai_response(content)
        parsed_fight_info = parse_battle_text(fight_info)

        save_battle_records_to_csv(fight_info, parsed_fight_info, chat_id, opponent_chat_id)
        if len(parsed_fight_info["Story"]) != 0 and len(parsed_fight_info["Mechanics"]) != 0:
            bot.send_message(chat_id=chat_id, text=generate_battle_message(parsed_fight_info))
            logger.warning(f"Chat_id {chat_id}: Could not parse properly fight info")
        else:
            bot.send_message(chat_id=chat_id, text=fight_info)

        time.sleep(10)

        bot.send_message(chat_id=chat_id, text=finish_campaign_message)

        logger.info(f"Chat_id {chat_id}: Campaign action complete")
        set_user_status(chat_id, "status", "Ready")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)


# NAME
def handle_reset_user_action(bot: Bot, chat_id: str, message_text: str):
    try:
        logger.info(f"Chat_id {chat_id}: Starting name action")
        if message_text.strip() == "/reset_user":
            logger.info(f"Chat_id {chat_id}: Reset action is completed. But nobody was reseted")
        else:
            user_chat_id = message_text[10:].strip()
            reset_user(user_chat_id)
            bot.send_message(chat_id=chat_id, text="User has been reseted.")

        logger.info(f"Chat_id {chat_id}: Reset action complete")
    except Exception as error:
        logger.error(f"Chat_ID {chat_id}: {error}")
        bot.send_message(chat_id=chat_id, text=error_message)
