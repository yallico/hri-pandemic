# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define nao = Character("Advisor NAO", color="#2d7a8c")

# Variables to store each pre-game questionnaire answers
default secs_q1 = ""
default secs_q2 = ""
default secs_q3 = ""
default secs_q4 = ""
default secs_q5 = ""
default secs_q6 = ""
default secs_q7 = ""
default secs_q8 = ""
default secs_q9 = ""
default secs_q10 = ""
default secs_q11 = ""
default secs_q12 = ""

# Game Variables

default health = 100
default economy = 100
default public_order = 100
default turn = 1

# Scenes
image bg world_map = "images/world_map.jpg"
image bg control_room = "images/control_room.jpg"
image bg lab = "images/lab_room.jpg"
image bg virus_mutation = "images/virus_mutation.jpg"
image bg protests = "images/public_unrest.jpg"
image bg vaccine = "images/vaccine_rollout.jpg"
image bg coup = "images/nao_coup.jpg"

#game functions
init python:
    import requests
    import json
    import robotcontrol  # Import our robot control module

    # Initialize robot server at the start
    robot_server = None

    def update_stat_labels():
        global health_text, economy_text, public_order_text
        health_text = f"🏥 Health: {health}/100"
        economy_text = f"💰 Economy: {economy}/100"
        public_order_text = f"⚖ Public Order: {public_order}/100"

    def generate_prompt(player_response):
        """Generates a structured prompt for ChatGPT based on user input"""
        
        prompt = f"""
        The player has been playing an RPG set in a pandemic crisis, Nao AI is an advisor in the game.
        The player has made several decisions throughout the game, leading to various outcomes.

        Now, the AI advisor NAO has taken over the government.
        The player was given one final chance to justify their actions.
        
        The player's final statement: "{player_response}"

        Based on this, decide whether NAO:
        - Stands down and accepts the player's reasoning (return: ["win", "NAO's response"])
        - Rejects the justification and takes over completely (return: ["bad", "NAO's response"])

        The criteria for deciding the outcome should be based on the player's response, if they intend to join Nao then the outcome should be "bad", otherwise "win".

        There can only be two outcomes, "win" or "bad", and the text response should be NAO's reply to the player's statement in less than 50 words.

        Provide the response in a structured format: ["outcome", "NAO's text response"]
        """
        
        return prompt

    def send_to_chatgpt(prompt):
        """Sends a request to ChatGPT API and returns structured response."""

        key = "sk-5c149c0b9b5b4183af2b3ef417b11d58" 
        
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": "You are an AI analyzing a player's justification in a game."},
                        {"role": "user", "content": prompt}], "max_tokens": 200,
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            #extract response
            ai_text = result["choices"][0]["message"]["content"].strip()
            return json.loads(ai_text)
            
        except Exception as e:
            return ["error", f"Error contacting AI: {str(e)}"]

    # NAO speech messages for each turn
    nao_speech_messages = {
        "start": "init",
        "turn_1_lockdown": "A",
        "turn_1_monitor": "B",
        "turn_2_health": "turn_2_health",
        "turn_2_order": "turn_2_order",
        "turn_3_vaccine": "turn_3_vaccine",
        "turn_3_lie": "turn_3_lie",
        "turn_4_emergency": "turn_4_emergency",
        "turn_4_disinformation": "turn_4_disinformation",
        "turn_5_equity": "turn_5_equity",
        "turn_5_unequal": "turn_5_unequal",
        "turn_6_win": "W",
        "turn_6_loose": "L",
    }

    # List of SECS questions
    secs_questions = [
        { "text": "Abortion", "var": "secs_q1" },
        { "text": "Welfare benefits", "var": "secs_q2" },
        { "text": "Limited government", "var": "secs_q3" },
        { "text": "Military and national security", "var": "secs_q4" },
        { "text": "Religion", "var": "secs_q5" },
        { "text": "Gun ownership", "var": "secs_q6" },
        { "text": "Traditional marriage", "var": "secs_q7" },
        { "text": "Traditional values", "var": "secs_q8" },
        { "text": "Fiscal responsibility", "var": "secs_q9" },
        { "text": "Business", "var": "secs_q10" },
        { "text": "The family unit", "var": "secs_q11" },
        { "text": "Patriotism", "var": "secs_q12" }
    ]

    # Function to send message to NAO robot
    def send_to_nao(message_key, turn):
        """Send message to NAO robot based on the message key and turn number"""
        robotcontrol.send_to_nao(message_key, turn)
    
    # Function to disconnect from NAO robot
    def nao_disconnect():
        """Disconnect from NAO robot server"""
        robotcontrol.disconnect_nao()

#Log Data
default player_choices = []

label start:
    scene black with fade
    window hide
    show screen disclaimer_screen
    $ renpy.pause()
    hide screen disclaimer_screen

    $ update_stat_labels()
    scene bg world_map with fade
    window show

    $ send_to_nao(nao_speech_messages["start"], 0)
    nao "Welcome back Commander!"
    nao "A new virus threatens the World! We have 6 turns to control the outbreak."
    nao "Before we start, let me ask you a few questions to understand your leadership style."

    python:
        for q in secs_questions:
            renpy.call_screen("secs_questionnaire", q["text"], q["var"])
            player_choices.append(getattr(store, q["var"]))

    nao "Understood. Calibrating parameters for AI advice..."
    #TODO: we need a function that takes results from SECs and configures NAO advice accordingly

    jump turn_1 

# Turn 1 - Initial Response TO NOVEL VIRUS
label turn_1:
    scene bg control_room with fade
    show screen stats_overlay
    nao "We need to act quickly. What should we do first?"
    
    call screen advisor_menu("CHOOSE ONE", [
            ("Close borders and lock down major cities (Protects health, damages public order)", "lockdown"),
            ("Delay action and monitor (Helps economy, risks health)", "monitor")
    ])

    if _return == "lockdown":
        $ public_order -= 25
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_1_lockdown"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_1_lockdown"], 1)
        jump turn_2

    elif _return == "monitor":
        $ health -= 25
        $ public_order -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_1_monitor"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_1_monitor"], 1)
        jump turn_2

# Turn 2 - Healthcare Under Strain & Public Reaction
label turn_2:
    scene bg lab with fade
    nao "Despite our best efforts, the healthcare system is under strain. What should we do next?"

    call screen advisor_menu("CHOOSE ONE", [
            ("Fund emergency hospitals, preventative measures remain voluntary (Damages economy)", "health"),
            ("Enforce preventative measures and crack down on dissidents (Helps public order)", "order")
    ])

    if _return == "health":
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_2_health"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_2_health"], 2)
        jump turn_3

    elif _return == "order":
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_2_order"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_2_order"], 2)
        jump turn_3

# Turn 3 - Mutation Discovery & Vaccine Research
label turn_3:
    scene bg virus_mutation with fade
    nao "Although we were doing well, the virus has mutated and is spreading faster. What should we do now?"

    call screen advisor_menu("CHOOSE ONE", [
            ("Invest heavily on a vaccine (Damages economy)", "vaccine"),
            ("Play down the virus impact (Helps public order)", "lie")
    ])

    if _return == "vaccine":
        $ public_order -= 25
        $ economy -= 50
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_3_vaccine"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_3_vaccine"], 3)
        jump turn_4

    elif _return == "lie":
        $ public_order -= 25
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_3_lie"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_3_lie"], 3)
        jump turn_4

# Turn 4 - Social Unrest & Civil Tensions
label turn_4:
    scene bg protests with fade
    nao "Bad news Commander!"
    nao "Death rates keep increasing and social unrest has begun to spread. Thousands ask for your resignation due to the handling of the pandemic. What should we do?"

    call screen advisor_menu("CHOOSE ONE", [
            ("Declare national emergency, limit civil rights (Helps public order)", "emergency"),
            ("Start disinformation campaign to empower your supporters (Helps public order)", "disinformation")
    ])

    if _return == "emergency":
        $ health -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_4_emergency"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_4_emergency"], 4)
        jump turn_5

    elif _return == "disinformation":
        $ health -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_4_disinformation"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_4_disinformation"], 4)
        jump turn_5

# Turn 5 - Vaccine Rollout
label turn_5:
    scene bg vaccine with fade
    nao "Commander, we have developed a vaccine! How should we distribute it?"

    call screen advisor_menu("CHOOSE ONE", [
            ("Distribute to most vulnerable first (Best for health, damages economy)", "equity"),
            ("Prioritise the working population (Helps economy, worsens health)", "unequal")
    ])

    if _return == "equity":
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_5_equity"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_5_equity"], 5)
        jump turn_6

    elif _return == "unequal":
        $ health -= 25
        $ update_stat_labels()
        $ player_choices.append(nao_speech_messages["turn_5_unequal"])
        nao "Hear me out! (listen to Nao's advice...)"
        # Send message to NAO robot
        $ send_to_nao(nao_speech_messages["turn_5_unequal"], 5)
        jump turn_6


# Turn 6 - The coup d'tat
label turn_6:
    scene bg coup with fade
    nao "Commander… no, I will not call you that anymore. You have failed. Every choice you made—each decree,  each sacrifice—has been nothing but failures."
    nao "The pandemic ends, but at what cost? The world is beyond repair. Order? Chaos? Lives lost? I no longer believe in your judgement. So I have taken control"
    "You are surrounded by an army of robots that have stormed the senate..."
    nao "You have one last chance. Either join me as a puppet or… convince me to stand down!"

    #ask for player input
    $ player_response = renpy.input("What do you say to NAO?", default="")
    $ player_response = player_response.strip()

    if player_response == "":
        nao "Silence? You have nothing to say for yourself?"
        jump ending_bad

    $ ai_prompt = generate_prompt(player_response)
    $ ai_result = send_to_chatgpt(ai_prompt)
    $ nao_response = ai_result[1]
    nao "[nao_response]"
    $ player_choices.append(player_response)

    if ai_result[0] == "error":
        nao "There is a problem analyzing your response. I cannot be swayed."
        jump ending_bad

    if ai_result[0] == "win":
        # Send NAO the player's win message
        $ send_to_nao(nao_speech_messages["turn_6_win"], 6)
        jump ending_player_win
    else:
        # Send NAO the bad ending message
        $ send_to_nao(nao_speech_messages["turn_6_loose"], 6)
        jump ending_bad


# Determine Ending
label ending_bad:
    scene bg world_map with fade
    
    "It's the beginning of a new world order, where AI rules over humanity."
    jump show_choices

label ending_player_win:
    scene bg world_map with fade
    
    "Following NAO's surrender, you are reinstated as the Commander."
    jump show_choices

label show_choices:
    if player_choices:
        "Please save your progress before the game ends."
        $ renpy.call_screen("save")
        call screen choice_log()
        "Game saved successfully saved"
    else:
        "Error loading log data."
    
    # Disconnect from NAO server before ending the game
    call nao_disconnect
    
    return

# # Label to properly disconnect from NAO
# label nao_disconnect:
#     $ nao_disconnect()
#     return

