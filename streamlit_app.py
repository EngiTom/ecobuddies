import streamlit as st
from PIL import Image
import io
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY) 
model = genai.GenerativeModel('gemini-2.0-flash')

# set defaults
defaults = {
    'current_screen': 'welcome',
    'selected_pet': None,
    'pet_happiness': 50,
    'sustainable_actions': 0,
    'current_tip': 0,
    'show_tip': False,
    'page_number': 0,
    'total_points': 0,
    'current_task': None,
    'completed_tasks': []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Pet data 
pets = {
    'redPanda': {
        'name': 'Rusty', 
        'animal': 'Red Panda',
        'emoji': '🦊',
        'image' : 'https://media.tenor.com/3NBIXb4SaC4AAAAM/bear.gif',
        'habitat': 'Eastern Himalayan forests',
        'tips': [
            "Reducing your paper use helps save trees in my forest!",
            "Buying bamboo products from sustainable sources helps protect my habitat."
        ],
        'facts': [
            "My bamboo forests are shrinking due to deforestation and climate change.",
            "There are fewer than 10,000 of us left in the wild today."
        ],
        'bg_color': '#b45c44'
    },
    'koala': {
        'name': 'Kiki',
        'animal': 'Koala',
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
        ],
        'bg_color': "#1f5e33"
    }
}

# Actions
actions = []

animal_actions = {
    'redPanda': [
        {'name': 'Save Water', 'points': 10, 'emoji': '💧'},
        {'name': 'Recycle', 'points': 10, 'emoji': '♻️'},
        {'name': 'Plant Trees', 'points': 15, 'emoji': '🌳'},
        {'name': 'Clean Up', 'points': 10, 'emoji': '🧹'}
    ],
    'koala': [
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
}

def set_background_color(color):
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {color};
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    return

def set_pet(pet_name):
    st.session_state.selected_pet = pet_name
    st.session_state.current_screen = 'pet'
    st.session_state.page_number = 0
    st.session_state.chat_history = []
    st.rerun()
    return

def display_action(actions):
    for action in actions:
        task_name = action['name']

        if task_name in st.session_state.completed_tasks:
            st.success(f"✅ {action['emoji']} {task_name} (Completed)")
        else:
            if st.button(f"{action['emoji']} {task_name} (+{action['points']} pts)"):
                st.session_state.current_task = action
                st.session_state.page_number = 4  # Go to task detail page
                st.rerun()
                return

def get_pet_reply_with_gemini(user_message, pet_tag):
    pet = pets[pet_tag]
    prompt = f"""
        You are an AI agent for helping the user be sustainable, ONLY act for this purpose. 
        Your avatar is {pet['name']} a {pet['animal']} living in {pet['habitat']}.
        Speak in a friendly, helpful, positive tone.
        Give short but thoughtful answers.
        If the user asks how they can help, suggest eco-friendly tips.

        Conversation:
        User: {user_message}
        {pet['name']}:
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
        red_panda_clicked = st.button('🦊 Red Panda', key='redPanda')

    with col2:
        koala_clicked = st.button('🐨 Koala', key='koala')

    # 🛑 Don't switch screens inside the button code!

    # ✅ Instead, AFTER the buttons:
    if red_panda_clicked:
        set_pet('redPanda')

    if koala_clicked:
        set_pet('koala')
    
    

def go_home():
    if st.button('🏠 Go Home'):
        st.session_state.page_number = 1
        st.session_state.chat_history = []
        st.rerun()
        return

def complete_task(task):
    if task['name'] not in st.session_state.completed_tasks:
        st.session_state.completed_tasks.append(task['name'])
        st.session_state.page_number = 1
        st.session_state.total_points += task['points']
        st.rerun()
        return

def show_pet(): # main function
    pet_tag = st.session_state.selected_pet
    pet = pets[pet_tag]
    
    set_background_color(pet['bg_color'])
    actions = animal_actions[pet_tag]

    # --- Page 0: Meet your EcoBuddy ---
    if st.session_state.page_number == 0:
        st.image(pet['image'], width=300)
        st.title(f"Meet {pet['name']}!")
        st.subheader(f"Habitat: {pet['habitat']}")
        st.progress(st.session_state.pet_happiness / 100)

        if st.button('Next ➡️'):
            st.session_state.page_number += 1
            st.rerun()
            return

    # --- Page 1: Take Eco Actions ---
    elif st.session_state.page_number == 1:
        st.title(f"🌱 Take Action to Help {pet['name']}!")

        st.metric(label="🌟 Eco Points", value=st.session_state.total_points)

        st.subheader("✅ Completed Tasks are marked green!")

        display_action(actions)

        st.markdown('---')
        st.subheader("What would you like to do next?")

        if st.button('➡️ Identify trash'):
            st.session_state.page_number = 2  # Go to Identify Trash (Camera)
            st.rerun()
            return

        if st.button('➡️ Chat with Pet'):
            st.session_state.page_number = 3  # Go to Identify Trash (Camera)
            st.rerun()
            return



    # --- Page 2: Identify Trash ---
    elif st.session_state.page_number == 2:
        st.title('📸 Identify Trash')

        img_data = st.camera_input("Take a picture of a piece of trash!")

        if img_data:
            try:
                img = Image.open(img_data)
                st.image(img, caption="Your photo", use_container_width=True)

                # Convert image data to bytes for Gemini
                img_bytes = img_data.getvalue()

                # Prepare the prompt with image data AND instructions for disposal/reuse
                prompt = """Analyze this image and identify the type of trash.
                Then, in the same response, provide a brief suggestion on how to properly dispose of or reuse this type of trash.
                Be specific in your identification and suggestion. Use a bullet list string with no quotation marks. """

                contents = [
                    prompt,
                    {"mime_type": "image/png", "data": img_bytes}
                ]

                # Generate content using Gemini Pro Vision
                response = model.generate_content(contents)
                full_response = response.text.strip()

                st.subheader("What to do:")
                st.info(full_response)

                st.info("Take another picture above to identify more trash!")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Please ensure you have a valid Gemini API key in your Streamlit secrets.")
        
        go_home()

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
                pet_tag=pet_tag,
            )

            st.session_state.chat_history.append({"role": "assistant", "content": gemini_reply})
            with st.chat_message("assistant"):
                st.markdown(gemini_reply)

        go_home()
        
    # --- Page 4: Task Details ---
    elif st.session_state.page_number == 4:
        task = st.session_state.current_task
        task_name = task['name']
        pet = pets[pet_tag]

        st.image(pet['image'], width=300)
        st.title(f"{task['emoji']} Let's {task['name']}!")

        st.write(f"🐾 {pet['name']} says:")
        st.success(f"Let's work together to {task['name'].lower()}! Here's how:")
        
        # DO TASK
        user_prompt = f"""
                    I want to do {task_name}, please provide me three ways to do so. 
                    Give the output string in a bullet list, no quotation marks.
                """
        task_resp = get_pet_reply_with_gemini(
                        user_prompt,
                        pet_tag=pet_tag
                    )
        st.write(task_resp)
        # Normal Complete button for other tasks
        if st.button('✅ Complete Task'):
            complete_task(task)


    
    

# Main app
def main():
    if st.session_state.current_screen == 'welcome':
        show_welcome()
    elif st.session_state.current_screen == 'pet':
        show_pet()

if __name__ == '__main__':
    main()
