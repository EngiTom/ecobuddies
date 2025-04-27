import streamlit as st
import streamlit.components.v1 as components  
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
genai.configure(api_key=GEMINI_API_KEY)
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
    'polarBear': {
        'name': 'Snowflake',
        'animal': 'Polar Bear',
        'image' : 'PolarBear.gif',
        'habitat': 'the Arctic',
        'bg_color': '#032b44',
        'emoji': '🐻‍❄️',

    },
    'koala': {
        'name': 'Kiki',
        'animal': 'Koala',
        'image' : "Koala.gif",
        'habitat': 'Eucalyptus forests of Eastern Australia',
        'bg_color': "#7DAA92",
        "emoji": '🐨',
    },

    'whale': {
        'name': 'Nautica',
        'animal': 'Humpback Whale',
        'image' : "Whale.gif",
        'habitat' :'ocean',
        'bg_color': "#12204b",
        'emoji': '🐋',
    }
}

# Actions
actions = []

animal_actions = {
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

user_info = {
    'age': 30,
    'student': False,
    'income_level': "Average",
    'commitment_level': "Average"
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

def get_pet_reply_with_gemini(user_message, pet_tag, chat_history=None):
    pet = pets[pet_tag]
    conversation_context = ""
    if chat_history:
        # Skip the most recent user message as we'll add it separately
        for msg in chat_history[:-1]:  
            role = "User" if msg["role"] == "user" else f"{pet_tag}"
            conversation_context += f"{role}: {msg['content']}\n\n"
        
    prompt = f"""You are an AI agent for helping the user be sustainable, ONLY act for this purpose. 
Your avatar is {pet['name']} a {pet['animal']} living in {pet['habitat']}.
The user has the following characteristics: {str(user_info)}. Give short but thoughtful answers which take the user's characteristics into account. 
Speak in a friendly, helpful, positive tone.
If the user asks how they can help, suggest eco-friendly tips.
If you begin to get into an interactive mode with the user, make full use of the chat history and tell them what to do next or explain reasonings along the way. 

Previous conversation:
{conversation_context}

User's latest message: {user_message}
        
Respond as {pet['name']}, maintaining character and giving educational guidance on sustainability."""
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
    if st.button('EcoBuddies Quiz'):
        # Transition to the next screen (welcome screen)
        st.session_state.current_screen = 'quiz'
        st.rerun() 

def show_quiz():
    st.title("Tell us about yourself!")
    st.subheader("This helps us customize your EcoBuddies experience (this will be shared with Google but is not tied to your name)")
    
    # Age input using a slider
    age = st.slider("How old are you?", min_value=2, max_value=100, value=39, step=1)
    
    # Student status using radio buttons
    student_status = st.radio("Are you a student?", ["Yes", "No"], index=1)
    
    # Income level using selectbox
    income_level = st.selectbox("What's your income level?", 
                              ["Low", "Below Average", "Average", "Above Average", "High"],
                              index=2)
    
    # Commitment level using a slider with custom labels
    commitment_level = st.selectbox("How much time can you commit to sustainability?",
                                ["A few minutes", "Occasionally", "Blend it in", "Throughout the day", "24/7"],
                                index=2)
    topics_of_interest = st.selectbox("Which topic are you most interested in?",
                                ["Climate change", "Pollution", "Consumerism", "Agriculture", "Energy"],
                                index=2)
    
    # Update the global user_info
    if st.button('Continue to EcoBuddies'):
        # Update the global dictionary
        st.session_state.user_info = {
            'age': age,
            'student': student_status == "Yes",
            'income_level': income_level,
            'commitment_level': commitment_level,
            'topics_of_interest': topics_of_interest
        }
        
        # Transition to the next screen
        st.session_state.current_screen = 'welcome'
        st.rerun()
        
    # Optional: Display current selections at the bottom
    with st.expander("Current selections", expanded=True):
        st.write(f"Age: {age}")
        st.write(f"Student: {student_status}")
        st.write(f"Income Level: {income_level}")
        st.write(f"Commitment Level: {commitment_level}")
        st.write(f"Topics of Interest: {topics_of_interest}")

def show_welcome():
    st.title('🌿 Welcome to EcoBuddies! 🌿')
    st.subheader('Choose your EcoBuddy!')

    # Pet data
    pets = [
        {'name': 'Polar Bear', 'id': 'polarBear', 'image': 'PolarBear.gif'}, 
        {'name': 'Koala', 'id': 'koala', 'image': 'Koala.gif'}, 
        {'name': 'Whale', 'id': 'whale', 'image': 'Whale.gif'}
    ]
    
    # Create columns dynamically based on number of pets
    cols = st.columns(len(pets))
    
    # Display each pet in its column
    for i, pet in enumerate(pets):
        with cols[i]:
            if st.button(f'Choose {pet["name"]}'):
                st.session_state.selected_pet = pet['id']
                st.session_state.current_screen = 'pet'
                st.session_state.page_number = 0
                st.session_state.chat_history = []
                st.rerun()
            
            # Convert GIF to base64 and display
            gif_base64 = image_to_base64(pet['image'])
            st.markdown(clickable_image(gif_base64, key=pet['id'], pet_name=pet['name']), unsafe_allow_html=True)

       
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

def get_pet_intro_gemini(pet_tag):
    msg = """Briefly and concisely describe your NATURAL HABITAT, a THREAT, and a FUN FACT in a bullet list."""
    return get_pet_reply_with_gemini(msg, pet_tag)

def get_first_chat_with_gemini(pet_tag):
    msg = """Suggest 3 mundane adventure-like activities the user can do in a sustainable way like going to the grocery store in a multi-step interactive way,
asking pointed questions about the information provided. Let the user choose among the 3 activities and take into account how much time they can commit each day.
Make sure to include something that could be related to the user's topics of interest based on the information above. 

For example, ask the user how they would like to commute to the store then what they want to buy at the grocery store
in a natural flowing way. Take into account the background of the user."""
    return get_pet_reply_with_gemini(msg, pet_tag)

def show_pet(): # main function
    pet_tag = st.session_state.selected_pet
    pet = pets[pet_tag]
    
    set_background_color(pet['bg_color'])
    actions = animal_actions[pet_tag]

    # --- Page 0: Meet your EcoBuddy ---
    if st.session_state.page_number == 0:
        gif_base64 = image_to_base64(pet['image'])
        st.markdown(clickable_image(gif_base64, key=pet_tag, pet_name=pet['name']), unsafe_allow_html=True)
        
        st.title(f"Meet {pet['name']}!")
        resp = get_pet_intro_gemini(pet_tag)
        st.markdown(resp)

    if st.button('Next ➡️'):
        st.session_state.page_number += 1
        st.rerun()


    # --- Page 1: Take Eco Actions ---
    elif st.session_state.page_number == 1:
        # Convert GIF to base64 and display
        gif_base64 = image_to_base64(pet['image'])
        st.markdown(clickable_image(gif_base64, key=pet_tag, pet_name=pet['name']), unsafe_allow_html=True)

        st.title(f"🌱 Take Action to Help {pet['name']}!")

        #Eco points 
        import streamlit.components.v1 as components

        eco_points = st.session_state.total_points 
        max_points = 550

        progress = min(eco_points / max_points, 1.0)
        progress_percentage = int(progress * 100)

        bar_color = "#FFA500" if eco_points < max_points else "#00C851"

        html_code = f""" 
    <div style="background-color: lightgray; border-radius: 25px; padding: 5px; height: 40px;">
       <div style="
            background-color: {bar_color};
            width: 0%;
            height: 30px;
            border-radius: 20px;
            animation: fillAnimation 2s ease-in-out forwards;
            position: relative;
          ">
         </div> 
        <div style="
            position: absolute;
             top; 50%;
            left: 50%;
            transform: translate(-50%,-50%);
            font-weight: bold;
            color: black;
            font-size: 16px;
        ">
        {eco_points} / {max_points} Happiness Points
      </div>
    </div>

    <style>
    @keyframes fillAnimation {{
      from {{ width: 0%; }}
      to {{ width: {progress_percentage}%; }}
     }}
    </style>
     """
        components.html(html_code, height=70)

        st.subheader("✅ Completed Tasks are marked green!")

        display_action(actions)

        st.markdown('---')
        st.subheader("What would you like to do next?")

        if st.button('➡️ Identify trash'):
            st.session_state.page_number = 2  # Go to Identify Trash (Camera)
            st.rerun()
            return

        if st.button('🗝 Interactive Adventure!'):
            st.session_state.page_number = 3  # Go to Adventure
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
        st.title(f"💬 Chat with {pet['name']} {pet['emoji']}")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # do first prompt to user
        if len(st.session_state.chat_history) == 0:
            first_chat = get_first_chat_with_gemini(pet_tag=pet_tag)
            st.session_state.chat_history.append({"role": "assistant", "content": first_chat})

        # Display existing chat messages
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar=pet['emoji'] if msg["role"] == "assistant" else None):
                st.markdown(msg["content"])

        if "clear_chat_input" in st.session_state and st.session_state.clear_chat_input:
            st.session_state.chat_input = ""
            st.session_state.clear_chat_input = False

        user_input = st.text_input(f"Talk to {pet['name']}", key="chat_input")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            gemini_reply = get_pet_reply_with_gemini(
                user_message=user_input,
                pet_tag=pet_tag,
                chat_history=st.session_state.chat_history
            )

            st.session_state.chat_history.append({"role": "assistant", "content": gemini_reply})

            st.session_state.clear_chat_input = True
            st.rerun()

        go_home()
        
    # --- Page 4: Task Details ---
    elif st.session_state.page_number == 4:
        task = st.session_state.current_task
        task_name = task['name']
        pet = pets[pet_tag]

        gif_base64 = image_to_base64(pet['image'])
        st.markdown(clickable_image(gif_base64, key=pet_tag, pet_name=pet['name']), unsafe_allow_html=True)

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
            
            if idx > 0:
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
                    followup_prompt = f"Explain HOW to '{way}' in a practical, simple, understandable way."
                    followup_response = get_pet_reply_with_gemini(followup_prompt, pet_tag=pet_tag)
                    st.success(f"**How:** {followup_response}")

                if st.session_state["why_clicked"] == idx:
                    followup_prompt = f"Explain WHY it matters to '{way}' for the environment or WHY it works."
                    followup_response = get_pet_reply_with_gemini(followup_prompt, pet_tag=pet_tag)
                    st.info(f"**Why:** {followup_response}")

        # Normal Complete button for other tasks
        if st.button('✅ Complete Task'):
            complete_task(task)
    

# Main app
def main():
    # if 'current_screen' not in st.session_state:
    #     st.session_state.current_screen = 'gif'  # Start with the GIF screen
    curr_screen = st.session_state.current_screen
    if curr_screen == 'gif':
        show_gif()  # Show the GIF screen
    elif curr_screen == 'quiz':
        show_quiz()
    elif curr_screen == 'welcome':
        show_welcome()
    elif curr_screen == 'pet':
        show_pet()

if __name__ == '__main__':
    main()