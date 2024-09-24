def have_a_chat_time(state):
    print("\n>>>> NODE: have_a_chat_time")



    return {
        "lines": lines,
        "vote": vote,
        "vote_history": vote_history,
        "is_discussion_finished": is_discussion_finished,
        "is_round_finished": is_round_finished,
        "round_loop_count": state["round_loop_count"] + 1,
    }

