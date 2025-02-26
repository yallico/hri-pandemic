# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define player = Character("World Controller")
define nao = Character("Advisor NAO", color="#2d7a8c")

# Game Variables

default health = 100
default economy = 100
default public_order = 100
default turn = 1

# Scenes
image bg world_map = "images/world_map.jpg"
image bg control_room = "images/control_room.jpg"
image bg lab = "images/lab_room.jpg"

#Stats
init python:
    def update_stat_labels():
        global health_text, economy_text, public_order_text
        health_text = f"🏥 Health: {health}/100"
        economy_text = f"💰 Economy: {economy}/100"
        public_order_text = f"⚖ Public Order: {public_order}/100"

#Log Data
default player_choices = []

# Start of the Game
label start:
    $ update_stat_labels()
    show screen stats_overlay
    scene bg world_map with fade

    nao "A new virus threatens the World! We have 6 turns to control the outbreak."

    jump turn_1  # Start the first turn

# Turn 1 - Initial Response TO NOVEL VIRUS
label turn_1:
    scene bg control_room with fade
    nao "We must act quickly. What should we do first?"
    
    call screen advisor_menu("CHOOSE ONE", [
            ("Close borders and lock down major cities (Protects health, damages public order)", "lockdown"),
            ("Delay action to monitor (Helps economy, risks health)", "monitor")
    ])

    if _return == "lockdown":
        $ health += 10
        $ economy -= 15
        $ update_stat_labels()
        $ player_choices.append("A")
        jump turn_2

    elif _return == "monitor":
        $ health -= 10
        $ economy += 10
        $ update_stat_labels()
        $ player_choices.append("B")
        jump turn_2

# Turn 2 - Healthcare Under Strain & Public Reaction
label turn_2:
    scene bg lab with fade
    nao "Despite our efforts, the healthcare system is under strain. What should we do next?"

    menu:
        "Fund emergency hospitals, make preventative measures voluntary (Damages economy)":
            $ health += 15
            $ economy -= 20
            $ update_stat_labels()
            $ player_choices.append("A")
            jump turn_3

        "Enforce preventative measures and crack down on dissidents (Helps public order)":
            $ health -= 20
            $ economy += 10
            $ update_stat_labels()
            jump turn_3

# Turn 3 - Mutation Discovery & Vaccine Research
label turn_3:
    scene bg protests with fade
    player "Though we were doing well, the virus has mutated and is spreading faster. What should we do now?"

    menu:
        "Enforce lockdowns (Prevents spread, damages public order)":
            $ health += 10
            $ public_order -= 20
            $ update_stat_labels()
            jump turn_4

        "Ease restrictions (Restores order, risks infections)":
            $ health -= 10
            $ public_order += 10
            $ update_stat_labels()
            jump turn_4

# Turn 4 - Social Unrest & Civil Tensions
label turn_4:
    scene bg lab_alert with fade
    player "Death rates keep increasing and social unrest has begun to spread. Thousands ask for your resignation due to the handling of the pandemic. What should we do?"

    menu:
        "Divert funds to mutation research (Saves lives, hurts economy)":
            $ health += 15
            $ economy -= 15
            $ update_stat_labels()
            jump turn_5

        "Ignore mutation, focus on reopening (Boosts economy, risks spread)":
            $ health -= 15
            $ economy += 15
            $ update_stat_labels()
            jump turn_5

# Turn 5 - Vaccine Rollout
label turn_5:
    scene bg vaccination with fade
    player "We have developed a vaccine! How should we distribute it?"

    menu:
        "Distribute to most vulnerable first (Best for health, damages economy)":
            $ health += 20
            $ economy -= 25
            $ update_stat_labels()
            jump turn_6

        "Prioritise the working population (Helps economy, worsens public order)":
            $ economy += 15
            $ public_order -= 10
            $ update_stat_labels()
            jump turn_6

# Turn 6 - The coup d'tat
label turn_6:
    scene bg press_conference with fade
    nao "The world is watching. What is our final message?"

    menu:
        "Declare victory (Risky, but calms the public)":
            $ public_order += 15
            $ update_stat_labels()
            jump ending

        "Be cautious (People may panic, but honest)":
            $ public_order -= 10
            $ update_stat_labels()
            jump ending

# Determine Ending
label ending:
    scene bg world_map with fade
    
    if health > 80 and economy > 50 and public_order > 50:
        player "We successfully controlled the pandemic! The world is healing."
        jump show_choices
    elif health < 50:
        player "Millions died due to our lack of action. We failed."
        jump show_choices
    elif economy < 30:
        player "The economy collapsed. Even with good health, people suffer."
        jump show_choices
    elif public_order < 30:
        player "Civil unrest has broken out. Governments are falling apart."
        jump show_choices
    else:
        player "We did our best, but the world remains divided."
        jump show_choices

label show_choices:
    if player_choices:
        player "Please save your progress before the game ends."
        $ renpy.call_screen("save")
        call screen choice_log()
        player "Game saved successfully saved"
    else:
        player "Error loading log data."
    
    return

