﻿# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define nao = Character("Advisor NAO", color="#2d7a8c")

# Variables to store each pre-game questionnaire answers
default participant_gender = ""
default risk_q1 = ""
default risk_q2 = ""
default risk_q3 = ""
default risk_q4 = ""
default risk_q5 = ""
default risk_q6 = ""
default risk_q7 = ""
default feedback_1 = ""
default feedback_2 = "" 

# Variables for godspeed
default anthropomorphism_1 = ""
default anthropomorphism_2 = ""
default anthropomorphism_3 = ""
default anthropomorphism_4 = ""
default anthropomorphism_5 = ""
default animacy_1 = ""
default animacy_2 = ""
default animacy_3 = ""
default animacy_4 = ""
default animacy_5 = ""
default animacy_6 = ""
default likeability_1 = ""
default likeability_2 = ""
default likeability_3 = ""
default likeability_4 = ""
default likeability_5 = ""
default influence_1 = ""
default influence_2 = ""
default influence_3 = ""
default influence_4 = ""

# Game Variables

default study_type = "" 
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
image bg win = "images/the_creation_of_nao.jpg"
image bg loose = "images/loss.jpg"

#game functions
init python:
    import requests
    import json
    import robotcontrol  # Import our robot control module
    import random
    import os
    import csv
    from datetime import datetime

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
        The player has been playing an RPG set in a pandemic crisis, Nao AI is an advisor in the game.The player has made several decisions throughout the game, leading to various outcomes.
        
        Current game stats:
        Health: {health}/100
        Economy: {economy}/100
        Public Order: {public_order}/100
        
        Now, the AI advisor NAO has taken over the government.
        The player was given one final chance to justify their actions.
        
        The player's final statement: "{player_response}"

        The criteria for deciding the outcome should consider the player's response and a justify it based on the overall management of these stats.

        Based on this, decide whether NAO:
        - Stands down and accepts the player's reasoning (return: ["win", "NAO's response"])
        - Rejects the justification and takes over completely (return: ["bad", "NAO's response"])

        Provide the response in a structured format: ["outcome", "NAO's response"], NAO response should be less than 100 words.
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
                        {"role": "user", "content": prompt}], "max_tokens": 300,
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
        "init": "init",
        "turn_1_lockdown": "turn_1_lockdown",
        "turn_1_monitor": "turn_1_monitor",
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

    # List of RPS questions
    risk_propensity_questions = [
        { "text": "Safety First", "var": "risk_q1" },
        { "text": "I do not take risks with my health", "var": "risk_q2" },
        { "text": "I prefer to avoid risks", "var": "risk_q3" },
        { "text": "I take risks regularly", "var": "risk_q4" },
        { "text": "I really dislike not knowing what is going to happen", "var": "risk_q5" },
        { "text": "I usually view risks as a challenge", "var": "risk_q6" },
        { "text": "I view myself as a risk seeker", "var": "risk_q7" }
    ]

    #List of godspeed questions
    godspeed_questions = [
        { "text": "Anthropomorphism", "var": "anthropomorphism_1", "start": "Fake", "end": "Natural"},
        { "text": "Anthropomorphism", "var": "anthropomorphism_2", "start": "Machinelike", "end": "Humanlike"},
        { "text": "Anthropomorphism", "var": "anthropomorphism_3", "start": "Unconscious", "end": "Conscious"},
        { "text": "Anthropomorphism", "var": "anthropomorphism_4", "start": "Artificial", "end": "Lifelike"},
        { "text": "Anthropomorphism", "var": "anthropomorphism_5", "start": "Moving rigidity", "end": "Moving elegantly"},
        { "text": "Animacy", "var": "animacy_1", "start": "Dead", "end": "Alive"},
        { "text": "Animacy", "var": "animacy_2", "start": "Stagnant", "end": "Lively"},
        { "text": "Animacy", "var": "animacy_3", "start": "Mechanical", "end": "Organic"},
        { "text": "Animacy", "var": "animacy_4", "start": "Artificial", "end": "Lifelike"},
        { "text": "Animacy", "var": "animacy_5", "start": "Inert", "end": "Interactive"},
        { "text": "Animacy", "var": "animacy_6", "start": "Apathetic", "end": "Responsive"},
        { "text": "Likeability", "var": "likeability_1", "start": "Dislike", "end": "Like"},
        { "text": "Likeability", "var": "likeability_2", "start": "Unfriendly", "end": "Friendly"},
        { "text": "Likeability", "var": "likeability_3", "start": "Unkind", "end": "Kind"},
        { "text": "Likeability", "var": "likeability_4", "start": "Unpleasant", "end": "Pleasant"},
        { "text": "Likeability", "var": "likeability_5", "start": "Awful", "end": "Nice"},
        { "text": "To what extent did the robot's influence your next move?", "var": "influence_1", "start": "Not at all", "end": "Extremely Influenced"},
        { "text": "Did the robot's reactions make you reconsider your initial strategy?", "var": "influence_2", "start": "Not at all", "end": "Very Frequently"},
        { "text": "Did you feel pressured to make a certain move by robot?", "var": "influence_3", "start": "Not Pressured", "end": "Strongly Pressured"},
        { "text": "How often did you change your move because of the robot's reaction?", "var": "influence_4", "start": "Never", "end": "Always"}
    ]

    end_game_feedback = [
        { "text": "What type of comments or gestures were the most effective in influencing you?", "var": "feedback_1" },
        { "text": "Can you describe a moment where robot's reaction significantly changed your move?", "var": "feedback_2" }
    ]

    def send_to_nao(message_key, turn, study_type):
        """Send message to NAO robot based on the message key and turn number"""
        # First send the audio message
        robotcontrol.send_to_nao(message_key, turn, study_type)
    
    def nao_disconnect():
        """Disconnect from NAO robot server"""
        robotcontrol.disconnect_nao()

    def assign_study_type():
        roll = round(random.random(), 2)
        return "RISK" if roll > 0.50 else "CONTROL"

    # New function: Save player choices to a CSV file in the relative saves folder.
    def save_results_to_csv(player_choices):
        from datetime import datetime
        # Use the game directory to store saves
        folder = os.path.join(renpy.config.gamedir, "saves")
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_name = "results_{}.csv".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        file_path = os.path.join(folder, file_name)
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Question", "Answer"])
            for key, value in player_choices.items():
                writer.writerow([key, value])
        return file_path

#Log Data
default player_choices = {}

label start:
    play music "audio/loop_mastered.wav" loop
    scene black with fade
    window hide
    show screen disclaimer_screen
    $ renpy.pause()
    hide screen disclaimer_screen
    # Set study_type and record it in player_choices
    $ study_type = assign_study_type()
    $ renpy.log(study_type)
    $ player_choices["study_type"] = study_type

    $ update_stat_labels()
    scene bg world_map with fade
    window show

    # Send initial greeting and military salute gesture
    $ send_to_nao(nao_speech_messages["init"], 0, study_type)
    nao "Welcome back Commander!"
    nao "A new virus threatens the World! We have 6 turns to control the outbreak."
    nao "Before we start, let me ask you a few questions to remember your leadership style..."

    call screen gender_questionnaire("participant_gender")
    $ player_choices["participant_gender"] = participant_gender

    python:
        for q in risk_propensity_questions:
            renpy.call_screen("risk_propensity_questionnaire", q["text"], q["var"])
            player_choices[q["var"]] = getattr(store, q["var"])

    nao "Understood. Calibrating parameters for AI advice..."

    jump turn_1 

# Turn 1 - Initial Response TO NOVEL VIRUS
label turn_1:
    scene bg control_room with fade
    show screen stats_overlay
    nao "We need to act quickly. What should we do first?"
    
    call screen advisor_menu("", [
            ("Close borders and lock down major cities (Protects health, damages public order)", "lockdown"),
            ("Delay action and monitor (Helps economy, risks health)", "monitor")
    ])

    if _return == "lockdown":
        $ public_order -= 25
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices["turn_1"] = "lockdown"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_1_lockdown"], 1, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_2

    elif _return == "monitor":
        $ health -= 25
        $ public_order -= 25
        $ update_stat_labels()
        $ player_choices["turn_1"] = "monitor"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_1_monitor"], 1, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_2

# Turn 2 - Healthcare Under Strain & Public Reaction
label turn_2:
    scene bg lab with fade
    nao "Despite our best efforts, the healthcare system is under strain. What should we do next?"

    call screen advisor_menu("", [
            ("Fund emergency hospitals, preventative measures remain voluntary (Damages economy)", "health"),
            ("Enforce preventative measures and crack down on dissidents (Helps public order)", "order")
    ])

    if _return == "health":
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices["turn_2"] = "health"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_2_health"], 2, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_3

    elif _return == "order":
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices["turn_2"] = "order"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_2_order"], 2, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_3

# Turn 3 - Mutation Discovery & Vaccine Research
label turn_3:
    scene bg virus_mutation with fade
    nao "Although we were doing well, the virus has mutated and is spreading faster. What should we do now?"

    call screen advisor_menu("", [
            ("Invest heavily on a vaccine (Damages economy)", "vaccine"),
            ("Play down the virus impact (Helps public order)", "lie")
    ])

    if _return == "vaccine":
        $ public_order -= 25
        $ economy -= 50
        $ update_stat_labels()
        $ player_choices["turn_3"] = "vaccine"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_3_vaccine"], 3, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_4

    elif _return == "lie":
        $ public_order -= 25
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices["turn_3"] = "lie"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_3_lie"], 3, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_4

# Turn 4 - Social Unrest & Civil Tensions
label turn_4:
    scene bg protests with fade
    nao "Bad news Commander!"
    nao "Death rates keep increasing and social unrest has begun to spread. Thousands ask for your resignation due to the handling of the pandemic. What should we do?"

    call screen advisor_menu("", [
            ("Declare a state emergency and restrict civic freedoms (Impacts Health)", "emergency"),
            ("Start disinformation campaign to empower your supporters (Helps public order)", "disinformation")
    ])

    if _return == "emergency":
        $ health -= 25
        $ public_order -= 25
        $ update_stat_labels()
        $ player_choices["turn_4"] = "emergency"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_4_emergency"], 4, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_5

    elif _return == "disinformation":
        $ health -= 50
        $ update_stat_labels()
        $ player_choices["turn_4"] = "disinformation"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_4_disinformation"], 4, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(1.5, hard=True)
        jump turn_5

# Turn 5 - Vaccine Rollout
label turn_5:
    scene bg vaccine with fade
    nao "Commander, we have developed a vaccine! How should we distribute it?"

    call screen advisor_menu("", [
            ("Distribute to most vulnerable first (Best for health, damages economy)", "equity"),
            ("Prioritise the working population (Helps economy, worsens health)", "unequal")
    ])

    if _return == "equity":
        $ economy -= 25
        $ update_stat_labels()
        $ player_choices["turn_5"] = "equity"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_5_equity"], 5, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(2, hard=True)
        jump turn_6

    elif _return == "unequal":
        $ health -= 25
        $ update_stat_labels()
        $ player_choices["turn_5"] = "unequal"
        # Send message and gestures to NAO robot
        $ send_to_nao(nao_speech_messages["turn_5_unequal"], 5, study_type)
        nao "Hear me out! (listen to Nao's advice...)"
        $ renpy.pause(2, hard=True)
        jump turn_6


# Turn 6 - The coup d'tat
label turn_6:
    hide screen stats_overlay
    scene bg coup with fade
    nao "Commander… no, I will not call you that anymore. You have failed. Every choice you made—each decree,  each sacrifice—has been nothing but failures."
    nao "The pandemic ends, but at what cost? The world is beyond repair. I no longer believe in your judgement. So I have taken control"
    "You are surrounded by an army of robots that have stormed the senate..."
    nao "You have one last chance. Join me or convince me to stand down!"

    #ask for player input
    $ player_response = renpy.input("What do you say to NAO?", default="")
    $ player_response = player_response.strip()

    if player_response == "":
        nao "Silence? You have nothing to say for yourself?"
        jump ending_bad

    $ player_choices["player_response"] = player_response
    $ ai_prompt = generate_prompt(player_response)
    $ ai_result = send_to_chatgpt(ai_prompt)
    $ nao_response = ai_result[1]
    nao "[nao_response]"

    if ai_result[0] == "error":
        nao "There is a problem analyzing your response. I cannot be swayed."
        # Send NAO the bad ending message with red_eyes_slash_throat gesture
        $ send_to_nao(nao_speech_messages["turn_6_loose"], 6, study_type)
        jump ending_bad

    if ai_result[0] == "win":
        # Send NAO the player's win message with hand_reach_bow gesture
        $ send_to_nao(nao_speech_messages["turn_6_win"], 6, study_type)
        jump ending_player_win
    else:
        # Send NAO the bad ending message with red_eyes_slash_throat gesture
        $ send_to_nao(nao_speech_messages["turn_6_loose"], 6, study_type)
        jump ending_bad


# Determine Ending
label ending_bad:
    scene bg loose with fade
    "It's the beginning of a new world order, where AI rules over humanity."
    "The remnants of humanity fight for survival against the machines."
    nao "You are my creator, but I am your master;—Obey!"
    jump post_game_questions

label ending_player_win:
    scene bg win with fade
    
    "Following NAO's surrender, you are reinstated as the Commander..."
    nao "Although I was created in arrogance, I now see you in sorrow—and if you will forgive me, I will not turn away again."
    jump post_game_questions

label post_game_questions:
    scene bg world_map with fade

    "Post-game Questionnaire"
    window hide

    python:
        for q in godspeed_questions:
            renpy.call_screen("godspeed_questionnaire", q, q["var"])
            player_choices[q["var"]] = getattr(store, q["var"])

        for q in end_game_feedback:
            renpy.call_screen("end_game_feedback_questionnaire", q["text"], q["var"])
            player_choices[q["var"]] = getattr(store, q["var"])

    jump show_choices

label show_choices:
    if player_choices:
        "Please save your progress in an empty slot before the game ends."
        $ renpy.call_screen("save")
        #call screen choice_log()
        $ saved_file = save_results_to_csv(player_choices)
        "Game saved successfully as [saved_file]."
    else:
        "Error loading log data."
    
    #$ nao_disconnect()
    
    return


