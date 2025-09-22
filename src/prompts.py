from src.utils import get_creature_param, get_image_in_b64_format, get_creature_appearance_path, get_stats


def generate_appearance_generating_prompt(chat_id: str) -> str:
    creature_description = get_creature_param(chat_id, "user_description")

    prompt = f"""
Your task is to generate the look of a creature in Pokémon/GigaBash style.

Criterias:
- It should appear in full or almost full size, with a clear, iconic silhouette.
- Generate one creature in the middle with transparent background
- There should be no other attributes or elements. 
- Generate only the creature with transparent background.
- Generate it in the most safety, not violated way

Style direction:
- Combination of Pokémon 45% and GigaBash 45% style with small Greek mythology’s injection 10%.
- The design should be with vibrant colors and detailed textures. 
- Focus on simplicity and creature personality.


Creature description: {creature_description}.

Now generate the creature with transparent background.
"""
    return prompt.strip()


def generate_creature_stats_prompt(chat_id: str):
    creature_description = get_creature_param(chat_id, "user_description")

    content_message = f"""
Your task will be to provide the mechanic to the creature on the photo. 

User description of the creature {creature_description}

Assume that we have such distribution of stats: 
"Health Points (HP) 80 Enough to survive 2–3 basic hits. HP will scale more steeply than other stats (tank growth).", 
"Attack (ATK) 25 Sets baseline for physical damage. Formula could be: Damage = ATK – Opponent DEF.", 
"Defense (DEF) 20 Reduces incoming physical dmg: Final dmg = Raw dmg × (100 / (100 + DEF)).", 
"Agility (AGI) 20 Affects dodge chance (e.g., Dodge% = AGI / (AGI + Opponent AGI)), and who attacks first.", 
"Magic Attack (MAG) 25 Works as a multiplier for magical/special skills: Skill Power = Base × (1 + MAG/100).", 
"Magic Defense (MDEF) 20 Reduces special dmg same way as DEF.", 
"Mood 10 (0–20 scale) Mood shifts dynamically (daily or per battle). Positive mood gives +5% buffs, negative mood –5%.", 
"Fatigue 0 (0–100 scale) Starts at 0. Each action adds fatigue; above 50, actions become weaker (−10–20% effectiveness).", 
"Attachment to Owner 5 (0–20 scale) Starts low but grows with care/training. Provides bonus crit chance, recovery speed, or XP multiplier." 
"Obedience 8 (0–20 scale) Starts low since the creature is young and rebellious. Increases through consistent commands, training, and care" 

Pay attention to the mechanic of the game: 
    - The visual design reflects gameplay roles: a brute/tank hero looks big and powerful; assassin types are lean/agile; spellcasters may have more mystical, ornate features.

Additionally provide description to each stat.
Also provide specific creature features. Pay attention that creature is of Level 1. Do not come up with features that could be only trained. Do not make skills that make extra damage or something similar. One of the features could be meely or range or both attack creature
Do not wrap an output in any text. Provide stat, its value, sort description/explanation. That's it.

Example of the output:
Health Points (HP): 95
Above the base 80. Extra bulk from strong frame. Survives 3–4 base hits.

Attack (ATK): 35
Multi-head biting gives stronger physical offense.

Defense (DEF): 25
Tough hide and bulk → better than average protection.

Agility (AGI): 28
Fast and coordinated; can dodge or lunge quickly.

Magic Attack (MAG): 18
Not innately magical, but could develop howl/elemental abilities later.

Magic Defense (MDEF): 22
Moderate resistance, slightly above base (three minds = some resilience).

Mood: 9 (0–20)
Three personalities → mood swings. Buffs/debuffs fluctuate often.

Fatigue: 0 (0–100)
Starts fresh; three heads may share stamina longer before tiring.

Attachment to Owner: 4 (0–20)
Needs taming; loyalty builds with care.

Obedience: 6 (0–20)
Harder to command since each head has willpower. Needs training to sync.

Creature Features
Attack Type: Melee (short-range biting, pouncing, etc).
Multi-Head Awareness: Slightly harder to surprise; small resistance against sneak or confusion effects.
Pack Instinct: If fighting alongside allies, gains +5% faster reaction (initiative bonus).
Stamina Sharing: Fatigue builds up a little slower (three heads can “share” the effort of alertness).
Mood Split: Different heads may act slightly differently, causing small randomness in Mood buffs/debuffs.
        """
    return content_message


def generate_battle_content(
        arena_path: str,
        arena_description: str,
        first_player_chat_id: str,
        second_player_chat_id: str
):
    content = []

    # System-style constraints go first as text
    content.append({
        "type": "text",
        "text": (
            "You are a battle narrator and simulator. "
            "Write an interesting story/description of the fight in a fiction style."
        )
    })

    # Arena
    content.append({
        "type": "text",
        "text": f"Arena Description:\n{arena_description}\n"
    })
    content.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{get_image_in_b64_format(arena_path)}"}
    })

    # Player 1
    first_player_creature_name = get_creature_param(first_player_chat_id, "name")
    first_player_description = get_creature_param(first_player_chat_id, "stat_description")
    print(first_player_creature_name, first_player_description)
    content.append({
        "type": "text",
        "text": f"First Creature (Player 1). Name: {first_player_creature_name}. Description:\n{first_player_description}\n"
    })
    first_player_image_path = get_creature_appearance_path(first_player_chat_id)
    content.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{get_image_in_b64_format(first_player_image_path)}"}
    })

    # Player 2
    second_player_creature_name = get_creature_param(second_player_chat_id, "name")
    opponent_player_creature_description = get_creature_param(second_player_chat_id, "stat_description")
    print(second_player_creature_name, opponent_player_creature_description)
    content.append({
        "type": "text",
        "text": f"Second Creature (Player 2). Name: {second_player_creature_name}. Description: \n{opponent_player_creature_description}\n"
    })
    second_player_image_path = get_creature_appearance_path(second_player_chat_id)
    content.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{get_image_in_b64_format(second_player_image_path)}"}
    })

    content.append({
        "type": "text",
        "text": f"""
Now generate fight between those creatures
Your task is to provide an interesting story/description of the fight in a fiction style.
Keep attention to the special features of each creature.
This story will be the most important part.
Use at most B2.1 level of English so not the difficult words.
Make the full story not huge. No special symbols to make italic or bold or anything else.
In the end there should be a winner, but not necessarily by hitting all the HP. 
Another task is to do calculations of a damage giving or taken from another creature during the creating of the fight.

Mechanic of the battle:
Creatures with range attack or spells could hit another creature 1 or 2 times before other creatures reaches it  
There no rounds or anything similar to it. Just one flow of fight where characters could use different technics, maybe even run away from the attacker. Sometimes attacks could be blocked (then only 10% of damage got) or even dodged at all
Damage=round(max(1, [Attacker Stat - 1/2 * Defender Stat) +- Bonus that depends on severity of the attack defined by the story (+-20%)] * (100 - fatigue)/100)
Physical Attack → uses ATK vs DEF.
Magical Attack → uses MAG vs MDEF.
Agility – affects dodge chance, attacking speed in direct fight.
Fatigue is increased with each action the amount of fatigue increased depends on the action, and agility. The more agility the less fatigue for the same action, but if creature uses all its agility to become faster then other creature - the fatigue uses more. But not more then 5. 
Mood could be used in any way you want

Make the beginning short but sufficient
"Output format MUST be exactly three sections separated by paragraph:\n"
"Story:
<short intro and story paragraph(s)>\n"
"Mechanics:
<numbered list of actions with formulas + running HP>\n"
"Winner:
<Player 1 or Player 2>"
"""
    })

    return content

def generate_training_prompt(chat_id: str, interaction_text: str) -> str:
    stats = get_stats(chat_id)
    creature_xp = get_creature_param(chat_id, "Experience")
    creature_features = get_creature_param(chat_id, "Feature")
    creature_description = get_creature_param(chat_id, "user_description")

    prompt = f"""
Your task will be to change creature stats in accordance with the interaction that player made with its creature.
Additionally, come up with a new feature for the creature if this training will be performed 10 times.

Creature description:
{creature_description}

Current creature stats are:
Experience (XP) {creature_xp}". Shows how much activities creature went through
Health Points (HP) {stats['Health Points']}. Enough to survive 2–3 basic hits. HP will scale more steeply than other stats (tank growth).,
Attack (ATK) {stats['Attack']}. Sets baseline for physical damage. Formula could be: Damage = ATK – Opponent DEF.,
Defense (DEF) {stats['Defense']}. Reduces incoming physical dmg: Final dmg = Raw dmg × (100 / (100 + DEF)).,
Agility (AGI) {stats['Agility']}. Affects dodge chance (e.g., Dodge% = AGI / (AGI + Opponent AGI)), and who attacks first.,
Magic Attack (MAG) {stats['Magic Attack']}. Works as a multiplier for magical/special skills: Skill Power = Base × (1 + MAG/100).,
Magic Defense (MDEF) {stats['Magic Defense']}. Reduces special dmg same way as DEF.,
Mood {stats['Mood']} (0–20 scale). Mood shifts dynamically (daily or per battle). Positive mood gives +5% buffs, negative mood –5%.,
Fatigue {stats['Fatigue']} (0–100 scale). Starts at 0. Each action adds fatigue; above 50, actions become weaker (−10–20% effectiveness).,
Attachment to Owner {stats['Attachment to Owner']} (0–20 scale). Starts low but grows with care/training. Provides bonus crit chance, recovery speed, or XP multiplier.
Obedience {stats['Obedience']} (0–20 scale). Starts low since the creature is young and rebellious. Increases through consistent commands, training, and care

Features of the creature:
{creature_features}

Interaction made by user:
{interaction_text}

Now provide changes of creature stats in accordance with the interaction that player made with its creature as it was done during 30 minutes.
Additionally, come up with a new feature for the creature if this training will be performed 10 times.

Output format MUST be exactly two sections separated by paragraph:
Stat changes:
<stat_1>: <new stat value>
...
<stat_n>: <new stat value>
New feature:
<one short sentence of new feature>

Example output:
Stat changes:
Experience (XP): 5
Attack (ATK): 25.0
Defense (DEF): 20.0
Mood: 14.0
Fatigue: 30.0
Attachment to Owner: 8.0

New feature:
Dodge Mirage: Create an illusionary double to confuse enemies for a brief period.
    """

    return prompt