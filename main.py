from LLM import answer_question

MAX_FOLLOW_UPS = 12

def main():
    follow_up_count = 0
    current_session_id = None
    print("Welcome to the AI Chatbot!")
    print("Type 'quit' to exit.\n")
    while True:
        if follow_up_count >= MAX_FOLLOW_UPS:
            print("\nYou have reached the maximum number of follow-ups (12) for this session.")
            user_satisfied = input("Are you satisfied with the answers? (yes/no): ").strip().lower()
            if user_satisfied in ["no", "n"]:
                print("Escalating this session to human support...")
                escalation_msg = {"role": "system", "content": "Session escalated to human support.", "timestamp": str(datetime.datetime.now(datetime.timezone.utc))}
                add_message_to_session(current_session_id, escalation_msg, escalation=True)
                print(f"Session {current_session_id} marked as escalated. Ending session.\n")
                current_session_id = None
                follow_up_count = 0
                continue
            else:
                print("Thank you for your feedback. Ending session.\n")
                break
        user_input = input("\nEnter your question: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        if user_input.strip():
            result = answer_question(current_session_id,user_input)
            current_session_id = result.get('session_id')
            follow_up_count += 1
        else:
            print("Please enter a valid question.")

if __name__ == "__main__":
    main()
