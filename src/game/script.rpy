# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define player = Character("World Controller")

# Game Variables

default health = 100
default economy = 100
default public_order = 100
default turn = 1

# Scenes
image bg world_map = "images/world_map.jpg"

#Stats
init python:
    def update_stat_labels():
        global health_text, economy_text, public_order_text
        health_text = f"🏥 Health: {health}/100"
        economy_text = f"💰 Economy: {economy}/100"
        public_order_text = f"⚖ Public Order: {public_order}/100"

# init -1 python:
#     update_stat_labels()

# Start of the Game
label start:
    $ update_stat_labels()
    show screen stats_overlay
    scene bg world_map with fade

    player "A new virus has emerged. You have 6 turns to control the outbreak."

    jump turn_1  # Start the first turn

# Turn 1 - Initial Response
label turn_1:
    scene bg crisis_meeting with fade
    player "We must act quickly. What should we do first?"
    
    menu:
        "Lock down major cities (Protects health, damages economy)":
            $ health += 10
            $ economy -= 15
            $ update_stat_labels()
            jump turn_2

        "Delay action to monitor (Helps economy, risks health)":
            $ health -= 10
            $ economy += 10
            $ update_stat_labels()
            jump turn_2

# Turn 2 - Vaccine Research
label turn_2:
    scene bg lab with fade
    player "Scientists need funding for a vaccine."

    menu:
        "Invest heavily (Speeds vaccine, hurts economy)":
            $ health += 15
            $ economy -= 20
            $ update_stat_labels()
            jump turn_3

        "Rely on natural immunity (Risky but saves money)":
            $ health -= 20
            $ economy += 10
            $ update_stat_labels()
            jump turn_3

# Turn 3 - Social Order
label turn_3:
    scene bg protests with fade
    player "People are protesting against restrictions."

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

# Turn 4 - Mutation Discovery
label turn_4:
    scene bg lab_alert with fade
    player "The virus has mutated! We need more research."

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
    player "The vaccine is ready. How should we distribute it?"

    menu:
        "Free for all (Best for health, damages economy)":
            $ health += 20
            $ economy -= 25
            $ update_stat_labels()
            jump turn_6

        "Charge for vaccines (Helps economy, worsens public trust)":
            $ economy += 15
            $ public_order -= 10
            $ update_stat_labels()
            jump turn_6

# Turn 6 - Final Decision
label turn_6:
    scene bg press_conference with fade
    player "The world is watching. What is our final message?"

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
        return
    elif health < 50:
        player "Millions died due to our lack of action. We failed."
        return
    elif economy < 30:
        player "The economy collapsed. Even with good health, people suffer."
        return
    elif public_order < 30:
        player "Civil unrest has broken out. Governments are falling apart."
        return
    else:
        player "We did our best, but the world remains divided."
        return
