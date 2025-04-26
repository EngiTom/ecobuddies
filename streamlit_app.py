import streamlit as st

# Initialize session state variables
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'welcome'
if 'selected_pet' not in st.session_state:
    st.session_state.selected_pet = None
if 'pet_happiness' not in st.session_state:
    st.session_state.pet_happiness = 50
if 'sustainable_actions' not in st.session_state:
    st.session_state.sustainable_actions = 0
if 'current_tip' not in st.session_state:
    st.session_state.current_tip = 0
if 'show_tip' not in st.session_state:
    st.session_state.show_tip = False
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []



import google.generativeai as genai

##genai.configure(api_key=""") Insert your API Key
model = genai.GenerativeModel('gemini-2.0-flash')


# Pet data
pets = {
    'redPanda': {
        'name': 'Rusty',
        'image' : 'https://media.tenor.com/3NBIXb4SaC4AAAAM/bear.gif',
        'habitat': 'Eastern Himalayan forests',
        'tips': [
            "Reducing your paper use helps save trees in my forest!",
            "Buying bamboo products from sustainable sources helps protect my habitat."
        ],
        'facts': [
            "My bamboo forests are shrinking due to deforestation and climate change.",
            "There are fewer than 10,000 of us left in the wild today."
        ]
    },
    'koala': {
        'name': 'Kiki',
        'emoji': '🐨',
        'image' : "https://media.tenor.com/5XKP-A-hxQIAAAAj/koala-day-koala-day-nft.gif",
        'habitat': 'Eucalyptus forests of Eastern Australia',
        'tips': [
            "Conserving water helps prevent drought that can lead to bushfires in my home.",
            "Reducing plastic waste helps protect wildlife in Australia like me!"
        ],
        'facts': [
            "Bushfires have destroyed millions of acres of my home.",
            "Urban development is breaking up our forests."
        ]
    }
}

# Actions
actions = []
panda_actions = [
    {'name': 'Save Water', 'points': 10, 'emoji': '💧'},
    {'name': 'Recycle', 'points': 10, 'emoji': '♻️'},
    {'name': 'Plant Trees', 'points': 15, 'emoji': '🌳'},
    {'name': 'Clean Up', 'points': 10, 'emoji': '🧹'}
]

koala_actions = [
    {'name': 'Bring Your Own Bag', 'points': 5, 'emoji': '🛍️'},
    {'name': 'Refill Your Water Bottle', 'points': 5, 'emoji': '🚰'},
    {'name': 'Turn Off Lights', 'points': 5, 'emoji': '💡'},
    {'name': 'Walk or Bike Instead of Driving', 'points': 10, 'emoji': '🚲'},
    {'name': 'Eat a Plant-Based Meal', 'points': 10, 'emoji': '🥗'},
    {'name': 'Pick Up 3 Pieces of Litter', 'points': 10, 'emoji': '🧹'},
    {'name': 'Unplug Electronics', 'points': 5, 'emoji': '🔌'},
    {'name': 'Take a 5-Minute Shower', 'points': 5, 'emoji': '🚿'},
    {'name': 'Recycle Something Today', 'points': 5, 'emoji': '♻️'},
    {'name': 'Educate a Friend', 'points': 5, 'emoji': '📚'},
]

def get_pet_reply_with_gemini(user_message, pet_name, pet_habitat):
    prompt = f"""
        You are {pet_name}, an endangered animal living in {pet_habitat}.
        Speak in a friendly, helpful, positive tone.
        Give short but thoughtful answers.
        If the user asks how they can help, suggest eco-friendly tips.

        Conversation:
        User: {user_message}
        {pet_name}:
        """
    response = model.generate_content(prompt)
    return response.text

# Perform an action
def perform_action(points):
    st.session_state.pet_happiness = min(100, st.session_state.pet_happiness + points)
    st.session_state.sustainable_actions += 1
    st.session_state.total_points += points  # 🆕 add points to total_points

    if st.session_state.sustainable_actions % 2 == 0:
        st.session_state.current_tip = st.session_state.sustainable_actions // 2 % len(pets[st.session_state.selected_pet]['tips'])
        st.session_state.show_tip = True


# Welcome screen
def show_welcome():
    st.title('🌿 EcoBuddies')
    st.header('Choose your EcoBuddy')

    col1, col2 = st.columns(2)

    # Create buttons
    with col1:
        red_panda_clicked = st.button('🦊 Red Panda', key='red_panda')

    with col2:
        koala_clicked = st.button('🐨 Koala', key='koala')

    # 🛑 Don't switch screens inside the button code!

    # ✅ Instead, AFTER the buttons:
    if red_panda_clicked:
        st.session_state.selected_pet = 'redPanda'
        st.session_state.current_screen = 'pet'
        st.session_state.page_number = 0
        st.session_state.chat_history = []
        st.rerun()

    if koala_clicked:
        st.session_state.selected_pet = 'koala'
        st.session_state.current_screen = 'pet'
        st.session_state.page_number = 0
        st.session_state.chat_history = []
        st.rerun()

def show_pet():
    pet = pets[st.session_state.selected_pet]
    if st.session_state.selected_pet == 'koala':
        actions = koala_actions
    else:
        actions = panda_actions

    # --- Page 0: Meet your EcoBuddy ---
    if st.session_state.page_number == 0:
        st.image(pet['image'], width=300)
        st.title(f"Meet {pet['name']}!")
        st.subheader(f"Habitat: {pet['habitat']}")
        st.progress(st.session_state.pet_happiness / 100)

        if st.button('Next ➡️'):
            st.session_state.page_number += 1
            st.rerun()

    # --- Page 1: Take Eco Actions ---
    elif st.session_state.page_number == 1:
        st.title('🌱 Take Action to Help Your Pet!')

        st.metric(label="🌟 Eco Points", value=st.session_state.total_points)

        st.subheader("✅ Completed Tasks are marked green!")

        for action in actions:
            task_name = action['name']

            if task_name in st.session_state.completed_tasks:
                st.success(f"✅ {action['emoji']} {task_name} (Completed)")
            else:
                if st.button(f"{action['emoji']} {task_name} (+{action['points']} pts)"):
                    st.session_state.current_task = action
                    st.session_state.page_number = 4  # Go to task detail page

        st.markdown('---')
        st.subheader("What would you like to do next?")

        if st.button('➕ Complete Another Task'):
            st.info("Pick another task above!")
            st.rerun()

        if st.button('➡️ Continue to Next Activity'):
            st.session_state.page_number = 2  # Go to Identify Trash (Camera)
            st.rerun()




    # --- Page 2: Identify Trash ---
    elif st.session_state.page_number == 2:
        st.title('📸 Identify Trash')

        img_data = st.camera_input("Take a picture of a piece of trash!")

        if img_data:
            from PIL import Image
            import random
            trash_types = ["Plastic Bottle ♻️", "Aluminum Can 🥫", "Paper 📰", "Food Waste 🍎", "Plastic Bag 🛍️"]
            result = random.choice(trash_types)

            img = Image.open(img_data)
            st.image(img, caption="Your photo", use_column_width=True)
            st.success(f"We think it's: **{result}**")

        if st.button('Next ➡️'):
            st.session_state.page_number += 1
            st.rerun()

    # --- Page 3: Chat with Pet ---
    elif st.session_state.page_number == 3:
        st.title(f"💬 Chat with {pet['name']}")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input(f"Talk to {pet['name']}")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # 🌟 Get Gemini-generated reply
            gemini_reply = get_pet_reply_with_gemini(
                user_input,
                pet_name=pet['name'],
                pet_habitat=pet['habitat']
            )

            st.session_state.chat_history.append({"role": "assistant", "content": gemini_reply})
            with st.chat_message("assistant"):
                st.markdown(gemini_reply)

        if st.button('🏠 Go Home'):
            st.session_state.current_screen = 'welcome'
            st.session_state.page_number = 0
            st.session_state.chat_history = []
    # --- Page 4: Task Details ---
    elif st.session_state.page_number == 4:
        task = st.session_state.current_task
        pet = pets[st.session_state.selected_pet]

        st.image(pet['image'], width=300)
        st.title(f"{task['emoji']} Let's {task['name']}!")

        st.write(f"🐾 {pet['name']} says:")
        st.success(f"Let's work together to {task['name'].lower()}! Here's how:")

        if task['name'] == 'Save Water':
            st.write("""
            - 🚿 Take shorter showers (5 minutes or less!)
            - 🪥 Turn off the tap when brushing your teeth.
            - 🌧️ Collect rainwater for watering plants.
            """)
        elif task['name'] == 'Recycle':
            st.write("""
            - ♻️ Separate paper, plastic, glass, and metals.
            - 🗑️ Find a local recycling center near you.
            - 🔍 Always check recycling symbols on packaging!
            """)
        elif task['name'] == 'Plant Trees':
            st.write("""
            - 🌱 Find native trees suited to your area.
            - 🧑‍🌾 Dig a small hole and gently place the sapling.
            - 💧 Water the tree regularly to help it grow strong!
            """)
        elif task['name'] == 'Clean Up':
            st.write("""
            - 🧤 Wear gloves for safety.
            - 🚮 Pick up trash during a walk or visit to a park.
            - 📸 Take a picture of the trash you collected!
            """)

            st.markdown("---")
            st.subheader("📸 Upload your trash cleanup photo!")

            # Show camera input
            img_data = st.camera_input("Take a picture of the trash you collected")

            # 🧠 Only allow task completion AFTER uploading a photo
            if img_data:
                if st.button('✅ Complete Task'):
                    if task['name'] not in st.session_state.completed_tasks:
                        st.session_state.completed_tasks.append(task['name'])

                    perform_action(task['points'])
                    st.success(f"You earned {task['points']} Eco Points! 🌟 Thanks for helping clean the planet! 🌎")
                    st.session_state.current_task = None
                    st.session_state.page_number = 1  # go back to Take Action page
            else:
                st.info("Please upload a trash cleanup photo to complete this task!")
        else:
            # Normal Complete button for other tasks
            if st.button('✅ Complete Task'):
                if task['name'] not in st.session_state.completed_tasks:
                    st.session_state.completed_tasks.append(task['name'])


    
    

# Main app
def main():
    if st.session_state.current_screen == 'welcome':
        show_welcome()
    elif st.session_state.current_screen == 'pet':
        show_pet()

if __name__ == '__main__':
    main()
