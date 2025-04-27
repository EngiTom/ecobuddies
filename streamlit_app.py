import streamlit as st
from PIL import Image
import io
import os
import google.generativeai as genai
import base64
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


model = genai.GenerativeModel('gemini-2.0-flash')

# set defaults
defaults = {
    'current_screen': 'gif',
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
        'image' : 'https://media.tenor.com/3NBIXb4SaC4AAAAM/bear.gif',
        'habitat': 'Eastern Himalayan forests',
        'bg_color': '#FFCCCB',
        'emoji': '🐼',
    },
    'polarBear': {
        'name': 'Snowflake',
        'animal': 'Polar Bear',
        'image' : 'https://media.tenor.com/3NBIXb4SaC4AAAAM/bear.gif',
        'habitat': 'the Artic',
        'bg_color': '#A4D8E1',
        'emoji': '🐻‍❄️',

    },
    'koala': {
        'name': 'Kiki',
        'animal': 'Koala',
        'image' : "https://media.tenor.com/5XKP-A-hxQIAAAAj/koala-day-koala-day-nft.gif",
        'habitat': 'Eucalyptus forests of Eastern Australia',
        'bg_color': "#7DAA92",
        "emoji": '🐨',
    },

    'whale': {
        'name': 'Nautica',
        'animal': 'Humpback Whale',
        'image' : "https://media1.tenor.com/m/L9MMAzLc5kAAAAAC/humpback-whale-whale.gif",
        'habitat' :'ocean',
        'bg_color': "#A4D8E1",
        'emoji': '🐋',
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
    ],
    'whale': [
        {'name': 'Reduce Plastic Use', 'points': 10, 'emoji': '🚯'},
        {'name': 'Use a Reusable Straw', 'points': 5, 'emoji': '🥤'},
        {'name': 'Support Ocean Conservation', 'points': 20, 'emoji': '🌊'},
        {'name': 'Participate in a Beach Cleanup', 'points': 15, 'emoji': '🏖️'},
        {'name': 'Educate Others About Marine Life', 'points': 10, 'emoji': '📚'},
        {'name': 'Choose Sustainable Seafood', 'points': 15, 'emoji': '🐟'},
        {'name': 'Reduce Water Usage', 'points': 10, 'emoji': '💧'},
        {'name': 'Use Eco-Friendly Products', 'points': 10, 'emoji': '🧴'}
    ],
    'polarBear' : [
    {'name': 'Switch to Renewable Energy', 'points': 20, 'emoji': '🌞'},
    {'name': 'Drive Less, Bike More', 'points': 15, 'emoji': '🚲'},
    {'name': 'Eat a Plant-Based Meal', 'points': 10, 'emoji': '🥗'},
    {'name': 'Reduce Home Heating Usage', 'points': 10, 'emoji': '🔥'},
    {'name': 'Vote for Climate Policies', 'points': 20, 'emoji': '🗳️'},
    {'name': 'Avoid Single-Use Plastics', 'points': 10, 'emoji': '🚯'},
    {'name': 'Unplug Devices', 'points': 5, 'emoji': '🔌'},
    {'name': 'Spread Awareness', 'points': 10, 'emoji': '📢'}
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
def style_image_buttons():
    st.markdown("""
        <style>
        div[data-testid="stButton"] > button {
            background-color: transparent;
            border: none;
            padding: 0;
        }
        div[data-testid="stButton"] > button:hover {
            transform: scale(1.05);
            transition: 0.3s;
        }
        </style>
    """, unsafe_allow_html=True)

def clickable_image(image_path, key, pet_name):
    button_html = f"""
    <style>
        .img-button-{key} {{
            background: none;
            border: none;
            padding: 0;
            cursor: pointer;
        }}
        .img-button-{key} img {{
            width: 200px;
            border-radius: 15px;
            transition: transform 0.3s;
        }}
        .img-button-{key}:hover img {{
            transform: scale(1.05);
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        }}
    </style>
    <button class="img-button-{key}" key="{key}" onClick="document.getElementById('{pet_name}').click();">
        <img src="data:image/png;base64,{image_path}" alt="{pet_name}">
    </button>
    """
    return button_html

def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
def show_gif():
    # Display the GIF only once
    st.image('https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnYyemNzbzlobHJhcXBudHp5Z3o4cncyM2lycnh6ODYzcmk2bmpzdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/sx0NAad049ow46AsGU/giphy.gif', width=700)
    # Provide the user with a button to continue
    st.markdown("""
        <style>
        .center-button {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .stButton > button {
            width: 200px; /* You can adjust the width */
            font-size: 18px;
        }
        </style>
    """, unsafe_allow_html=True)


    # Display the button only after GIF is shown
    if st.button('Continue to Buddies'):
        # Transition to the next screen (welcome screen)
        st.session_state.current_screen = 'welcome'
        st.rerun() 
def show_welcome():
    st.title('🌿 Welcome to EcoBuddies! 🌿')
    st.subheader('Choose your EcoBuddy!')

    # Convert images to base64
    polar_bear_img = image_to_base64('PolarBear.png')
    koala_img = image_to_base64('Koala.png')
    whale_img = image_to_base64('Whale.png')
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button('Choose Polar Bear'):
            st.session_state.selected_pet = 'polarBear'
            st.session_state.current_screen = 'pet'
            st.session_state.page_number = 0
            st.session_state.chat_history = []
            st.session_state.gif_shown = False
            st.session_state.current_screen = 'gif'
            st.rerun()

        # Display image
        st.markdown(clickable_image(polar_bear_img, key='polar', pet_name='Polar Bear'), unsafe_allow_html=True)

    with col2:
        if st.button('Choose Koala'):
            st.session_state.selected_pet = 'koala'
            st.session_state.current_screen = 'pet'
            st.session_state.page_number = 0
            st.session_state.chat_history = []
            st.session_state.gif_shown = False
            st.session_state.current_screen = 'gif'
            st.rerun()

        # Display image
        st.markdown(clickable_image(koala_img, key='koala', pet_name='Koala'), unsafe_allow_html=True)

    with col3:
        if st.button('Choose Whale'):
            st.session_state.selected_pet = 'whale'
            st.session_state.current_screen = 'pet'
            st.session_state.page_number = 0
            st.session_state.chat_history = []
            st.session_state.gif_shown = False
            st.session_state.current_screen = 'gif'
            st.rerun()

        # Display image
        st.markdown(clickable_image(whale_img, key='whale', pet_name='Whale'), unsafe_allow_html=True)

       
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

        user_input = st.text_input(f"Talk to {pet['name']}")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # 🌟 Get Gemini-generated reply
            gemini_reply = get_pet_reply_with_gemini(
                user_input,
                pet_tag=pet_tag,
            )

            st.session_state.chat_history.append({"role": "assistant", "content": gemini_reply, })
            animal = pet['animal']
            with st.chat_message("assistant", avatar=pet['emoji']):
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
        # Ask Gemini for 3 ways (already done)
        # --- inside your Page 4: Task Details ---

# Ask Gemini for 3 ways (already done)
        user_prompt = f"""
        I want to do {task_name}, please provide me three ways to do so.
        Give the output string in a bullet list, no quotation marks.
        """
        task_resp = get_pet_reply_with_gemini(user_prompt, pet_tag=pet_tag)

        # Split the response into separate suggestions
        ways = [way.strip("- ").strip("* ").strip() for way in task_resp.split("\n") if way.strip()]


        # Initialize clicked keys if they don't exist
        if "how_clicked" not in st.session_state:
            st.session_state["how_clicked"] = None
        if "why_clicked" not in st.session_state:
            st.session_state["why_clicked"] = None

        # Show each way with "How" and "Why" buttons
        for idx, way in enumerate(ways):
            st.markdown(f"**{way}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔎 How?", key=f"how_{idx}"):
                    st.session_state["how_clicked"] = idx
                    st.session_state["why_clicked"] = None  # reset
            with col2:
                if st.button(f"💡 Why?", key=f"why_{idx}"):
                    st.session_state["why_clicked"] = idx
                    st.session_state["how_clicked"] = None  # reset

            # If clicked, show the follow-up answer
            if st.session_state["how_clicked"] == idx:
                followup_prompt = f"Explain HOW to '{way}' in a practical, simple way."
                followup_response = get_pet_reply_with_gemini(followup_prompt, pet_tag=pet_tag)
                st.success(f"**How:** {followup_response}")

            if st.session_state["why_clicked"] == idx:
                followup_prompt = f"Explain WHY it matters to '{way}' for the environment."
                followup_response = get_pet_reply_with_gemini(followup_prompt, pet_tag=pet_tag)
                st.info(f"**Why:** {followup_response}")

        # Normal Complete button for other tasks
        if st.button('✅ Complete Task'):
            complete_task(task)


    
    

# Main app
def main():
    # if 'current_screen' not in st.session_state:
    #     st.session_state.current_screen = 'gif'  # Start with the GIF screen
    if st.session_state.current_screen == 'gif':
        show_gif()  # Show the GIF screen

    elif st.session_state.current_screen == 'welcome':
        show_welcome()
    elif st.session_state.current_screen == 'pet':
        show_pet()

if __name__ == '__main__':
    main()
