import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Custom function to display whole numbers in pie chart
def func(pct, allvals):
    absolute = int(round(pct / 100.0 * sum(allvals)))
    return "{:d}".format(absolute)

# Password dictionary for authorized users
passwords = {"Ali": "1234", "Adi": "5678", "Sahil": "chut"}

# Check if the CSV file exists, if not, create it
if not os.path.exists("scores.csv"):
    df = pd.DataFrame(columns=["Player 1", "Player 2", "Player 1 Score", "Player 2 Score", "Submitted By"])
    df.to_csv("scores.csv", index=False)

# Access code authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_user = None

# Password input (no need to select a name)
user_code = st.text_input("Enter your password", type="password")

if st.button("Submit Access Code"):
    # Authenticate based on the password dictionary
    for player_name, password in passwords.items():
        if user_code == password:
            st.session_state.authenticated = True
            st.session_state.current_user = player_name
            st.success(f"Access granted for {player_name}!")
            break
    else:
        st.error("Invalid access code.")

# Show all-time stats as soon as the correct password is entered
if st.session_state.authenticated:
    st.write(f"Welcome, {st.session_state.current_user}. You are now authorized to submit scores.")
    
    df = pd.read_csv("scores.csv")
    
    # Display summary statistics
    if not df.empty:
        # Most wins per player
        st.subheader("All-Time Most Wins")
        win_counts = pd.concat([df[df["Player 1 Score"] > df["Player 2 Score"]]["Player 1"],
                                df[df["Player 2 Score"] > df["Player 1 Score"]]["Player 2"]]).value_counts()
        st.bar_chart(win_counts)

    # Input form for submitting scores
    st.subheader("Submit New Score")
    player_options = ["Ali", "Adi", "Sahil"]

    # Select Player 1
    player_1 = st.selectbox("Player 1", [""] + player_options, key="player_1", index=0)

    # Filter player options for Player 2 (removing the selection for Player 1)
    if player_1:
        remaining_players = [player for player in player_options if player != player_1]
    else:
        remaining_players = player_options

    # Select Player 2
    player_2 = st.selectbox("Player 2", [""] + remaining_players, key="player_2", index=0)

    # Input for Player 1 score
    score_1 = st.number_input(f"{player_1} Score", min_value=0, key="score_1_input")

    # Input for Player 2 score
    score_2 = st.number_input(f"{player_2} Score", min_value=0, key="score_2_input")

    # Save data to CSV
    if st.button("Submit Score") and player_1 and player_2:
        new_data = {"Player 1": player_1, "Player 2": player_2, "Player 1 Score": score_1, "Player 2 Score": score_2, "Submitted By": st.session_state.current_user}
        df = pd.read_csv("scores.csv")
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv("scores.csv", index=False)
        st.success("Score submitted successfully!")

    # Display all-time games played and wins by each player
    st.subheader("All-Time Games Played and Wins by Each Player")

    # Games Played pie chart
    st.subheader("Games Played")

    # Count how many times each player appears in both Player 1 and Player 2 columns
    games_played = pd.concat([df["Player 1"], df["Player 2"]]).value_counts()

    # Plot the pie chart for games played with whole numbers
    fig1, ax1 = plt.subplots()
    ax1.pie(games_played, labels=games_played.index, autopct=lambda pct: func(pct, games_played), 
           colors=['#ff9999', '#66b3ff', '#99ff99'], startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.
    
    # Display the pie chart for games played
    st.pyplot(fig1)

    # Head-to-head record between two players
    st.subheader("Head-to-Head Record")
    player_1_stats = st.selectbox("Player 1 (Stats)", player_options, key="player_1_stats")
    player_2_stats = st.selectbox("Player 2 (Stats)", [player for player in player_options if player != player_1_stats], key="player_2_stats")

    if player_1_stats != player_2_stats:
        head_to_head = df[((df["Player 1"] == player_1_stats) & (df["Player 2"] == player_2_stats)) |
                          ((df["Player 1"] == player_2_stats) & (df["Player 2"] == player_1_stats))]

        # Wins for each player
        player_1_wins = len(head_to_head[(head_to_head["Player 1"] == player_1_stats) & (head_to_head["Player 1 Score"] > head_to_head["Player 2 Score"])]) + \
                        len(head_to_head[(head_to_head["Player 2"] == player_1_stats) & (head_to_head["Player 2 Score"] > head_to_head["Player 1 Score"])])

        player_2_wins = len(head_to_head[(head_to_head["Player 1"] == player_2_stats) & (head_to_head["Player 1 Score"] > head_to_head["Player 2 Score"])]) + \
                        len(head_to_head[(head_to_head["Player 2"] == player_2_stats) & (head_to_head["Player 2 Score"] > head_to_head["Player 1 Score"])])

        # Goals for/against
        player_1_goals_for = head_to_head[head_to_head["Player 1"] == player_1_stats]["Player 1 Score"].sum() + \
                             head_to_head[head_to_head["Player 2"] == player_1_stats]["Player 2 Score"].sum()

        player_1_goals_against = head_to_head[head_to_head["Player 1"] == player_1_stats]["Player 2 Score"].sum() + \
                                 head_to_head[head_to_head["Player 2"] == player_1_stats]["Player 1 Score"].sum()

        player_2_goals_for = head_to_head[head_to_head["Player 1"] == player_2_stats]["Player 1 Score"].sum() + \
                             head_to_head[head_to_head["Player 2"] == player_2_stats]["Player 2 Score"].sum()

        player_2_goals_against = head_to_head[head_to_head["Player 1"] == player_2_stats]["Player 2 Score"].sum() + \
                                 head_to_head[head_to_head["Player 2"] == player_2_stats]["Player 1 Score"].sum()

        st.write(f"{player_1_stats} Wins: {player_1_wins}, {player_2_stats} Wins: {player_2_wins}")
        st.write(f"{player_1_stats} Goals For: {player_1_goals_for}, Goals Against: {player_1_goals_against}")
        st.write(f"{player_2_stats} Goals For: {player_2_goals_for}, Goals Against: {player_2_goals_against}")
