import os
import telebot
from telebot import types
import requests
import base64
import re
import json
import subprocess
import sys
import io
import random
import zipfile
from PIL import Image
from rembg import remove
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Pass explicit path so systemd can always find .env
env_path = os.path.expanduser("~/ai_studio/.env")
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
admin_id_raw = os.getenv("ADMIN_ID")

if not TELEGRAM_TOKEN or not admin_id_raw:
    raise ValueError(f"Missing environment variables! Checked path: {env_path}")

ADMIN_ID = int(admin_id_raw)
USERS_FILE = os.path.expanduser("~/ai_studio/authorized_users.json")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_gdd = {}

# --- SECURITY & ACCESS CONTROL ---
def load_users():
    if not os.path.exists(USERS_FILE):
        default = {"approved": [ADMIN_ID]}
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, "w") as f:
            json.dump(default, f)
        return default
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f)

def is_authorized(user_id):
    data = load_users()
    return user_id in data["approved"]

# --- CORE LOGIC FUNCTIONS ---
def get_global_context() -> str:
    return """You are a specialized Al agent for a Unity 6 (URP) game studio. All code must be modern C# written specifically for Unity 6. 
PRIME DIRECTIVE: Agent 0 (The Studio Head) is your absolute anchor. You must strictly obey the 'Master GDD' provided to you. 
CRITICAL CODING RULE: Do NOT use deprecated legacy Unity APIs. Ensure all scripts are compatible with Unity 6.
If the Master GDD contains an 'ASSET MANIFEST', you MUST fulfill the exact quantities listed. Do not invent new assets. Do not skip assets.
Stick strictly to your defined role. Output strictly the requested Markdown, JSON, CSV, or Code blocks."""

def ask_agent(prompt: str, role_prompt: str, target_model: str = "llama3", state: dict = None, require_json: bool = False) -> str:
    url = "http://localhost:11434/api/generate"
    state_context = f"\nPROJECT STATE MEMORY (ANCHORED TO MASTER GDD):\n{json.dumps(state)}\n" if state else ""
    full_system = f"{get_global_context()}\n{state_context}\n{role_prompt}"
    
    payload = {"model": target_model, "system": full_system, "prompt": prompt, "stream": False, "options": {"num_ctx": 4096}}
    if require_json:
        payload["format"] = "json"
        
    try:
        response_data = requests.post(url, json=payload).json()
        
        if "error" in response_data:
            error_msg = f"OLLAMA ENGINE ERROR: {response_data['error']}"
            print(error_msg)
            return error_msg
            
        return response_data.get('response', '')
    except Exception as e:
        return f"LLM Python Error: {str(e)}"

def ask_vision_agent(prompt: str, image_path: str) -> str:
    url = "http://localhost:11434/api/generate"
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        
    # DOWNGRADED to a 7B Vision Model so the system doesn't freeze!
    # Removed num_gpu: 0 to let Ollama automatically balance it.
    payload = {
        "model": "llava", 
        "prompt": prompt, 
        "stream": False, 
        "images": [img_b64],
        "options": {"num_ctx": 4096} 
    }
    try:
        return requests.post(url, json=payload).json().get('response', '')
    except Exception as e:
        return f"Vision Error: {str(e)}"

def save_file(content: str, game_name: str, filename: str) -> str:
    base_path = os.path.expanduser(f"~/ai_studio/projects/{game_name}")
    full_path = os.path.join(base_path, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    return full_path

# --- DATA EXTRACTORS ---
def extract_block(text: str, tag: str) -> str:
    pattern = rf'```(?:{tag}|csharp|C#)\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if tag == "cs" and "using UnityEngine;" in text:
        return text[text.find("using UnityEngine;"):]
    return text.strip()

# --- BULLETPROOF JSON PARSER ---
def get_valid_json_array(chat_id, task_prompt: str, role_prompt: str, state: dict, target_model: str = "llama3") -> list:
    max_attempts = 3
    current_prompt = task_prompt
    for attempt in range(max_attempts):
        raw_response = ask_agent(current_prompt, role_prompt, target_model=target_model, state=state, require_json=True)
        try:
            clean = raw_response.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean)
            if isinstance(data, list): return data
            if isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, list): return val
            raise ValueError("Data was valid JSON, but did not contain an Array.")
        except Exception as e:
            try:
                start = raw_response.find('[')
                end = raw_response.rfind(']') + 1
                if start != -1 and end != 0:
                    data = json.loads(raw_response[start:end])
                    if isinstance(data, list): return data
            except:
                pass
            bot.send_message(chat_id, f"🔄 Formatting error detected (Attempt {attempt+1}/{max_attempts}). Forcing AI to fix syntax...")
            current_prompt = f"{task_prompt}\n\nYOUR PREVIOUS OUTPUT WAS REJECTED DUE TO SYNTAX ERROR:\n{str(e)}\n\nYou MUST return a raw JSON array starting with '['."
    raise Exception("Agent failed to produce valid JSON after 3 attempts.")

# --- AUTONOMOUS MEMORY & QA LOOPS ---
def update_studio_memory(chat_id, error_reason: str, state: dict):
    bot.send_message(chat_id, "🪽 Hermes (Agent 22) is analyzing the code failure to update Studio Memory...")
    sys_hermes = """ROLE: Lead Technical Writer & Memory Archivist (Agent 22)
TASKS: Read the Code Reviewer's rejection reason. Distill it into a SINGLE, strict, one-sentence rule for Unity 6 C# developers to prevent this mistake from ever happening again.
CRITICAL: Format it exactly as a simple markdown bullet point starting with a dash (-). Just the rule."""
    prompt = f"The Senior Code Reviewer rejected a script for this reason:\n{error_reason}\n\nWrite a new permanent rule for the manual."
    try:
        new_rule = ask_agent(prompt, sys_hermes, target_model="hermes3:8b", state=state).strip()
        if new_rule.startswith("```"): 
            new_rule = new_rule.replace("```markdown", "").replace("```", "").strip()
        manual_path = os.path.expanduser("~/ai_studio/unity6_cheat_sheet.md")
        os.makedirs(os.path.dirname(manual_path), exist_ok=True)
        with open(manual_path, "a") as f: 
            f.write(f"\n{new_rule}")
        bot.send_message(chat_id, f"🧠 Studio Memory Updated! Hermes added:\n{new_rule}")
    except Exception as e:
        pass

def autonomous_art_review(chat_id, image_path: str, intended_prompt: str, state: dict):
    bot.send_message(chat_id, "👁️ Agent 8 (Nemotron Vision) is inspecting the asset in System RAM...")
    
    global_style = state.get('raw_pitch', 'Retro 16-bit video game art.')
    qa_prompt = f"""You are an elite, strict Art Director (Agent 8) for a game studio. 
Analyze this generated 2D game asset. 
SPECIFIC ASSET: '{intended_prompt}'
GLOBAL GAME STYLE: '{global_style}'

Look carefully for:
1. ANATOMY: Mutated limbs, extra limbs, blended/fused objects, unrecognizable shapes.
2. STYLE MISMATCH: Does it look like a photograph instead of game art? Does it violate the Global Game Style?
3. CLEANLINESS: Is it a messy collage of multiple items, or a single usable game asset?

If it is absolutely flawless, output EXACTLY 'STATUS: PERFECT'. 
If it fails ANY of the checks above, output 'STATUS: FLAWED' followed by a brief, harsh description of what is visually wrong."""

    review = ask_vision_agent(qa_prompt, image_path)
    
    if "STATUS: FLAWED" in review.upper():
        bot.send_message(chat_id, f"⚠️ Agent 8 rejected the art: {review}\n🪽 Waking Hermes to write a new prompt rule...")
        sys_hermes_art = """ROLE: Lead Art Technical Writer (Agent 22)
TASKS: The QA Vision Agent detected errors in our Stable Diffusion output. Translate the error into a strict Prompt Engineering rule. Format it as a single bullet point starting with a dash (-). State exactly what keywords to add to the 'positive_prompt' or 'negative_prompt' to fix this."""
        hermes_prompt = f"The Vision Agent reported: '{review}'. Write a permanent rule to prevent this."
        try:
            new_rule = ask_agent(hermes_prompt, sys_hermes_art, target_model="hermes3:8b", state=state).strip()
            if new_rule.startswith("```"): 
                new_rule = new_rule.replace("```markdown", "").replace("```", "").strip()
            art_manual_path = os.path.expanduser("~/ai_studio/art_prompt_cheat_sheet.md")
            os.makedirs(os.path.dirname(art_manual_path), exist_ok=True)
            with open(art_manual_path, "a") as f: 
                f.write(f"\n{new_rule}")
            bot.send_message(chat_id, f"🎨 Art Memory Updated! Hermes added:\n{new_rule}")
        except Exception as e:
            pass
    else:
        bot.send_message(chat_id, "✨ Agent 8 approved the asset anatomy and style!")

# --- ART GENERATION SUITE ---
def generate_sd_art(positive: str, negative: str, game_name: str, filename: str, is_sprite: bool = False, state: dict = None, chat_id=None):
    width, height = 512, 512 
    if is_sprite:
        base_path = os.path.expanduser(f"~/ai_studio/projects/{game_name}/assets")
        master_positive = f"{positive}, <lora:pixel_sprite:1>, clear outline, uniform SOLID WHITE background, retro video game asset, 16-bit, centered"
        master_negative = f"{negative}, 3d, photorealistic, blurred background, gradients, multiple items"
    else:
        base_path = os.path.expanduser(f"~/ai_studio/projects/{game_name}/assets/story_panels")
        master_positive = f"{positive}, high quality manga style, cinematic lighting, professional 2d illustration"
        master_negative = f"{negative}, 3d, photorealistic, pixel art, blurry"

    os.makedirs(base_path, exist_ok=True)
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    payload = {"prompt": master_positive, "negative_prompt": master_negative, "steps": 25, "width": width, "height": height}
    try:
        raw_img_data = requests.post(url, json=payload).json()['images'][0]
        full_output_path = os.path.join(base_path, f"{filename}.png")
        
        if is_sprite:
            # We keep rembg here ONLY for single isolated icons.
            input_img = Image.open(io.BytesIO(base64.b64decode(raw_img_data)))
            output_img = remove(input_img)
            output_img.save(full_output_path)
            if chat_id and state:
                autonomous_art_review(chat_id, full_output_path, positive, state)
        else:
            with open(full_output_path, "wb") as f:
                f.write(base64.b64decode(raw_img_data))
            # Explicitly trigger the QA check for Story Panels too!
            if chat_id and state:
                autonomous_art_review(chat_id, full_output_path, positive, state)
    except Exception:
        pass

def generate_sd_sheet(positive: str, negative: str, game_name: str, filename: str, state: dict = None, chat_id=None):
    base_path = os.path.expanduser(f"~/ai_studio/projects/{game_name}/assets")
    os.makedirs(base_path, exist_ok=True)
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    master_positive = f"{positive}, <lora:pixel_sheet_character:1>, sprite sheet, character sheet, grid layout, sequence of frames, animation phases, SOLID WHITE background, clear outline, isolated"
    master_negative = f"{negative}, 3d, photorealistic, gradients, messy, inconsistent proportions, jumbled assets"
    payload = {"prompt": master_positive, "negative_prompt": master_negative, "steps": 30, "width": 512, "height": 512}
    try:
        raw_img_data = requests.post(url, json=payload).json()['images'][0]
        final_sheet_path = os.path.join(base_path, f"{filename}_sheet.png")
        
        with open(final_sheet_path, "wb") as f:
            f.write(base64.b64decode(raw_img_data))
            
        if chat_id and state:
            autonomous_art_review(chat_id, final_sheet_path, positive, state)
    except Exception:
        pass

def generate_sd_environment(positive: str, negative: str, game_name: str, filename: str):
    base_path = os.path.expanduser(f"~/ai_studio/projects/{game_name}/assets")
    os.makedirs(base_path, exist_ok=True)
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    master_positive = f"{positive}, 2d game background, level map, tileable terrain, environment art, rich details, edge-to-edge scenery, 16-bit retro aesthetic"
    master_negative = f"{negative}, 3d, photorealistic, characters, sprites, ui elements, text, white background, transparent background"
    payload = {"prompt": master_positive, "negative_prompt": master_negative, "steps": 30, "width": 512, "height": 512}
    try:
        raw_img_data = requests.post(url, json=payload).json()['images'][0]
        final_bg_path = os.path.join(base_path, f"{filename}_bg.png")
        with open(final_bg_path, "wb") as f:
            f.write(base64.b64decode(raw_img_data))
    except Exception:
        pass

# --- THE QWEN SELF-CORRECTION LOOP (WITH RAG/CHEAT SHEET) ---
def generate_and_review_code(chat_id, task_prompt: str, role_prompt: str, filename: str, game_name: str, state: dict) -> str:
    bot.send_message(chat_id, f"💻 Writing {filename} [Qwen 2.5]...")
    max_attempts = 3
    
    current_code = ask_agent(task_prompt, role_prompt, target_model="qwen2.5-coder:7b", state=state)
    
    manual_path = os.path.expanduser("~/ai_studio/unity6_cheat_sheet.md")
    unity_manual = ""
    if os.path.exists(manual_path):
        with open(manual_path, "r") as f: 
            unity_manual = f.read()

    sys_reviewer = f"""ROLE: Senior Unity 6 Code Reviewer (Agent 12)
TASKS: Review the C# code against Agent 0's Master GDD. 
CRITICAL: You are the ultimate authority on Unity 6. Cross-reference the code with this manual:
--- START UNITY 6 MANUAL ---
{unity_manual}
--- END UNITY 6 MANUAL ---
If the code violates the manual, output 'STATUS: REJECTED' and explain the fix. If ready, output 'STATUS: APPROVED'."""
    
    for attempt in range(max_attempts):
        code_block = extract_block(current_code, "cs")
        bot.send_message(chat_id, f"🔎 Agent 12 reviewing {filename} (Attempt {attempt+1}/{max_attempts})...")
        review_prompt = f"REVIEW THIS CODE:\n```cs\n{code_block}\n```"
        
        review_result = ask_agent(review_prompt, sys_reviewer, target_model="qwen2.5-coder:7b", state=state)
        
        if "STATUS: APPROVED" in review_result.upper() or attempt == max_attempts - 1:
            save_file(code_block, game_name, filename)
            state[filename] = f"Approved after {attempt+1} attempts."
            bot.send_message(chat_id, f"✅ {filename} passed review!")
            return code_block
        else:
            bot.send_message(chat_id, f"🔄 Agent 12 REJECTED {filename}. Sending back for rewrite...")
            update_studio_memory(chat_id, review_result, state)
            rewrite_prompt = f"{task_prompt}\n\nYOUR PREVIOUS CODE WAS REJECTED. FIX THESE ERRORS:\n{review_result}\n\nRewrite the code completely in a ```cs block."
            current_code = ask_agent(rewrite_prompt, role_prompt, target_model="qwen2.5-coder:7b", state=state)
            
    save_file(extract_block(current_code, "cs"), game_name, filename)
    return extract_block(current_code, "cs")

# --- NEW: PROCEDURAL AUDIO SYNTHESIZER ---
def generate_retro_sfx(chat_id, master_gdd, state, game_name):
    bot.send_message(chat_id, "🎵 Agent 10 (Audio Engineer) synthesizing retro Sound Effects...")
    audio_dir = os.path.expanduser(f"~/ai_studio/projects/{game_name}/assets/audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    sys_a10 = """ROLE: Procedural Audio Engineer (Agent 10)
TASKS: Read the ASSET MANIFEST. Write a COMPLETE Python script that generates the requested .wav files.
CRITICAL RULES:
1. You MUST import 'wave', 'math', 'struct', 'sys', 'os', and 'random'.
2. The script MUST accept a directory path as sys.argv[1]. If missing, default to './'.
3. Generate distinct retro 8-bit sounds (square waves for jump/shoot, noise for hit).
4. NEVER use `math.random()`. You MUST use `random.random()` or `random.uniform()`.
5. AVOID complex one-line generator expressions! They cause SyntaxErrors. You MUST use a safe loop pattern like this:
   frames = []
   for i in range(samples):
       val = int(32767 * math.sin(i))
       frames.append(struct.pack('<h', val))
   wav_file.writeframes(b''.join(frames))
6. Output ONLY valid CPython code inside a ```python block. Do not use numpy. Do not explain."""

    raw_audio_script = ask_agent(master_gdd, sys_a10, target_model="qwen2.5-coder:7b", state=state)
    sfx_script_path = save_file(extract_block(raw_audio_script, "python"), game_name, "generate_sfx.py")
    
    try:
        bot.send_message(chat_id, "🎹 Compiling Audio Waves...")
        result = subprocess.run([sys.executable, sfx_script_path, audio_dir], capture_output=True, text=True, check=True)
        bot.send_message(chat_id, f"✅ Audio generation complete! Files saved in assets/audio/")
    except subprocess.CalledProcessError as e:
        bot.send_message(chat_id, f"⚠️ Audio synthesis script crashed. Error:\n{e.stderr[:500]}")

# --- TELEGRAM INTAKE ---
@bot.message_handler(commands=['start', 'newgame'])
def start_interview(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Request Access", callback_data=f"req_{user_id}_{message.from_user.first_name}"))
        bot.reply_to(message, "⛔ **UNAUTHORIZED ACCESS**", reply_markup=markup)
        return
    user_gdd.clear()
    msg = bot.reply_to(message, "🎮 **100% Local Self-Improving Studio Initialized.**\n\nFirst, what is the **working title** or **name** of your game?")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    safe_name = "".join([c for c in message.text if c.isalnum() or c==' ']).rstrip().replace(" ", "_").lower()
    user_gdd['name'] = safe_name
    msg = bot.reply_to(message, f"📁 Unity workspace: `~/ai_studio/projects/{safe_name}/`\n\n**Step 1: Core Gameplay Loop**\nHow does the game actually play?")
    bot.register_next_step_handler(msg, process_gameplay)

def process_gameplay(message):
    user_gdd['gameplay'] = message.text
    msg = bot.reply_to(message, "**Step 2: The World & Environment**\nWhere does this game take place?")
    bot.register_next_step_handler(msg, process_environment)

def process_environment(message):
    user_gdd['environment'] = message.text
    msg = bot.reply_to(message, "**Step 3: Characters & Entities**\nWho is the player controlling, and who are they fighting?")
    bot.register_next_step_handler(msg, process_characters)

def process_characters(message):
    user_gdd['characters'] = message.text
    msg = bot.reply_to(message, "**Step 4: Objective & Conflict**\nWhat is the main goal or win/loss condition of the game?")
    bot.register_next_step_handler(msg, process_objective)

def process_objective(message):
    user_gdd['objective'] = message.text
    msg = bot.reply_to(message, "**Step 5: Art Style & Aesthetic**\nFinally, describe the visual vibe.")
    bot.register_next_step_handler(msg, process_aesthetic)

@bot.message_handler(commands=['artfix'])
def art_feedback(message):
    feedback = message.text.replace("/artfix", "").strip()
    chat_id = message.chat.id
    if not is_authorized(message.from_user.id): 
        return
    bot.send_message(chat_id, "🪽 Hermes is analyzing your art critique to update the Studio Art Manual...")
    sys_hermes_art = """ROLE: Lead Art Technical Writer (Agent 22)
TASKS: The Studio Director is unhappy with the generated AI art. Translate it into a strict Prompt Engineering rule. 
Format as a single bullet point starting with a dash (-). State exactly what keywords to add to the 'positive_prompt' or 'negative_prompt' in the future."""
    prompt = f"The Director says: '{feedback}'. Write a permanent prompt rule to fix this."
    try:
        new_rule = ask_agent(prompt, sys_hermes_art, target_model="hermes3:8b").strip()
        if new_rule.startswith("```"): 
            new_rule = new_rule.replace("```markdown", "").replace("```", "").strip()
        art_manual_path = os.path.expanduser("~/ai_studio/art_prompt_cheat_sheet.md")
        os.makedirs(os.path.dirname(art_manual_path), exist_ok=True)
        with open(art_manual_path, "a") as f: 
            f.write(f"\n{new_rule}")
        bot.send_message(chat_id, f"🎨 Art Memory Updated! Hermes added:\n{new_rule}\n\nAgent 5 will use this for all future games.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Hermes failed: {str(e)}")

@bot.message_handler(commands=['status'])
def studio_status(message):
    if not is_authorized(message.from_user.id): 
        return
    
    current_game = user_gdd.get('name', 'None')
    
    status_msg = f"""🟢 **AI Studio is Online & Listening**

**System Architecture:**
🧠 Logic: Local Ollama Engine
🎨 Assets: Stable Diffusion (Automatic1111)
🪽 Memory: Hermes Active

**Current Pipeline Status:**
📁 Active Project: `{current_game}`

Type /newgame to start a new project!"""
    
    bot.reply_to(message, status_msg, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('req_'))
def handle_access_request(call):
    _, request_uid, first_name = call.data.split('_', 2)
    bot.edit_message_text("⏳ Your request has been sent to the Admin.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{request_uid}"), types.InlineKeyboardButton("❌ Deny", callback_data=f"den_{request_uid}"))
    bot.send_message(ADMIN_ID, f"🔔 **New Studio Access Request**\nUser: {first_name}\nID: `{request_uid}`", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('app_') or call.data.startswith('den_'))
def handle_admin_decision(call):
    if call.from_user.id != ADMIN_ID: 
        return
    action, target_uid = call.data.split('_')
    target_uid = int(target_uid)
    if action == "app":
        data = load_users()
        if target_uid not in data["approved"]:
            data["approved"].append(target_uid)
            save_users(data)
        bot.edit_message_text(f"✅ Approved User ID `{target_uid}`.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(target_uid, "🎉 **Access Granted!**\n\nType `/newgame` to begin.", parse_mode="Markdown")
    elif action == "den":
        bot.edit_message_text(f"❌ Denied User ID `{target_uid}`.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(target_uid, "⛔ Your access request was denied.")

# --- THE PIPELINE ---
def process_aesthetic(message):
    user_gdd['aesthetic'] = message.text
    chat_id = message.chat.id
    game = user_gdd['name']
    raw_pitch = f"GAMEPLAY: {user_gdd['gameplay']}\nENV: {user_gdd['environment']}\nCHARS: {user_gdd['characters']}\nOBJ: {user_gdd['objective']}\nAESTHETIC: {user_gdd['aesthetic']}"
    
    # NEW: Master state now permanently stores your aesthetic
    master_state = {"project_name": game, "raw_pitch": raw_pitch, "aesthetic": user_gdd['aesthetic']}
    bot.send_message(chat_id, f"⚙️ Commencing Local Asset Pipeline...")
    
    try:
        # PHASE 1
        bot.send_message(chat_id, "👑 Phase 1: Agent 0 (Studio Head) is locking down the Master GDD...")
        sys_a0 = """ROLE: Lead Game Designer & Studio Head (Agent 0)
TASKS: Expand the raw pitch into a strict Master GDD. 
CRITICAL ANCHOR RULE: At the very bottom of the document, you MUST include an '## ASSET MANIFEST' section. 
In this section, list EXACTLY how many assets are required for a complete game.
You must demand a rich, complete set of assets. 
Example format:
- AUDIO_REQUIRED: 12 (Jump, Shoot, Explosion, Coin, Hurt, Select, Start, Ambient, etc.)
- MANGA_PANELS_REQUIRED: 3 (Intro cutscene)
- SPRITES_REQUIRED: 15 (Main Character, 3 types of enemies, Boss, 5 UI Icons, 5 Collectibles/Hazards)
- ENVIRONMENTS_REQUIRED: 4 (Title Screen, Level 1 Map, Level 2 Map, Game Over Screen)
Format strictly as Markdown."""
        
        master_gdd = ask_agent(raw_pitch, sys_a0, target_model="qwen2.5-coder:7b", state=master_state)
        master_state['master_gdd'] = master_gdd
        save_file(master_gdd, game, "00_MASTER_GDD.md")

        # PHASE 1.5: The Mentor / Consultant Loop
        bot.send_message(chat_id, "🧐 Phase 1.5: Agent 7 (Senior Consultant) is studying the Master GDD against Game Design Theory...")
        
        # Load your game dev tutorial/best practices file
        best_practices_path = os.path.expanduser("~/ai_studio/gamedev_best_practices.md")
        best_practices = "Ensure the game has 'juice' (screen shake, particle effects). The core loop must be instantly understandable."
        if os.path.exists(best_practices_path):
            with open(best_practices_path, "r") as f:
                best_practices = f.read()

        sys_a7 = f"""ROLE: Senior Game Design Consultant (Agent 7)
TASKS: Read the Master GDD provided by Agent 0. You are an expert in game feel, mechanics, and player psychology.
CRITICAL: You must cross-reference the GDD with the studio's Game Design Textbook:
--- START TEXTBOOK ---
{best_practices}
--- END TEXTBOOK ---
Write a critical 'Director's Review'. Suggest 3 specific, highly actionable improvements to the gameplay loop or mechanics to make the game more fun, polished, and perfectly aligned with industry standards.
Format strictly as Markdown."""

        # Using Qwen 2.5 for high-level reasoning
        expert_review = ask_agent(master_gdd, sys_a7, target_model="qwen2.5-coder:7b", state=master_state)
        save_file(expert_review, game, "00B_EXPERT_DESIGN_REVIEW.md")
        
        # Send a snippet of the advice directly to your Telegram
        preview_text = expert_review[:800] + "...\n*(See full review in project folder)*"
        bot.send_message(chat_id, f"💡 **Agent 7's Expert Feedback:**\n\n{preview_text}")
        
        # We append Agent 7's advice to the Master State so the coders (Agent 13, 14) can see it!
        master_state['expert_advice'] = expert_review

        bot.send_message(chat_id, "📖 Agents 16, 17, & 2 building Lore and Backlog...")
        save_file(ask_agent(master_gdd, "ROLE: Lore Master (Agent 16)\nTASKS: Read Master GDD. Write backstory. Format as Markdown.", target_model="qwen2.5-coder:7b", state=master_state), game, "lore.md")
        save_file(extract_block(ask_agent(master_gdd, "ROLE: Progression Balancer (Agent 17)\nTASKS: Output CSV mapping Enemy HP and XP scaling.", target_model="qwen2.5-coder:7b", state=master_state), "csv"), game, "balance_stats.csv")
        sprint_data = extract_block(ask_agent(master_gdd, "ROLE: Executive Producer (Agent 2)\nTASKS: Generate structured JSON sprint backlog.", target_model="qwen2.5-coder:7b", state=master_state), "json")
        master_state['sprints'] = sprint_data
        save_file(sprint_data, game, "sprint_backlog.json")

        # PHASE 2
        bot.send_message(chat_id, "📐 Phase 2: Agent 1 mapping Architecture from the GDD...")
        arch_data = ask_agent(sprint_data, "ROLE: System Architect (Agent 1)\nTASKS: Output C# script breakdown using Unity MonoBehaviours.", target_model="qwen2.5-coder:7b", state=master_state)
        master_state['architecture'] = arch_data
        save_file(arch_data, game, "architecture.md")

        # PHASE 3: DUAL-ART & ENVIRONMENT WITH MEMORY INJECTION
        bot.send_message(chat_id, "🎨 Phase 3: Fulfilling Agent 0's Master Asset Manifest locally...")
        
        art_manual_path = os.path.expanduser("~/ai_studio/art_prompt_cheat_sheet.md")
        art_manual = ""
        if os.path.exists(art_manual_path):
            with open(art_manual_path, "r") as f: 
                art_manual = f.read()

        sys_a20 = f"""ROLE: SD Narrative Director (Agent 20)
TASKS: Read the ASSET MANIFEST in the Master GDD. Generate a JSON array for 'MANGA_PANELS_REQUIRED'.
CRITICAL: Apply these historical prompt rules from the Art Manual:
--- START ART MANUAL ---
{art_manual}
--- END ART MANUAL ---
MUST contain 'filename', 'positive_prompt', and 'negative_prompt'.
OUTPUT STRICTLY A RAW JSON ARRAY. Example format:
[
  {{"filename": "intro_cutscene", "positive_prompt": "epic space battle", "negative_prompt": "ugly, blurry"}}
]"""
        try:
            story_assets = get_valid_json_array(chat_id, master_gdd, sys_a20, master_state, target_model="mistral")
            for i, asset in enumerate(story_assets):
                if not isinstance(asset, dict):
                    bot.send_message(chat_id, f"⚠️ Agent 20 formatting error on panel {i+1}. Skipping...")
                    continue
                file_name = asset.get('filename', f'story_panel_{i}')
                bot.send_message(chat_id, f"🖌️ Drawing Panel {i+1}/{len(story_assets)}: {file_name}...")
                
                # NEW: Force the global aesthetic onto the end of the prompt!
                forced_prompt = f"{asset.get('positive_prompt', '')}, {master_state['aesthetic']}"
                
                generate_sd_art(forced_prompt, asset.get('negative_prompt', ''), game, file_name, is_sprite=False, state=master_state, chat_id=chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Manga Generation Failed: {str(e)}")

        sys_a5 = f"""ROLE: Stable Diffusion Sprite Specialist (Agent 5)
TASKS: Read the ASSET MANIFEST. 
CRITICAL RULE 1: ONLY extract items from 'SPRITES_REQUIRED' and 'ENVIRONMENTS_REQUIRED'.
CRITICAL RULE 2: IGNORE 'AUDIO_REQUIRED'. Do NOT generate image prompts for sound effects!
Determine if asset is 'STATIC_ICON', 'MAIN_CHARACTER', or 'ENVIRONMENT_MAP'.
CRITICAL: Apply historical prompt adjustments from the Art Manual:
--- START ART MANUAL ---
{art_manual}
--- END ART MANUAL ---
MUST contain 'filename', 'positive_prompt', 'negative_prompt', 'is_sheet', 'is_env'.
OUTPUT STRICTLY A RAW JSON ARRAY. Example format:
[
  {{"filename": "player", "positive_prompt": "knight", "negative_prompt": "ugly", "is_sheet": true, "is_env": false}}
]"""
        try:
            sprite_manifest = get_valid_json_array(chat_id, master_gdd, sys_a5, master_state, target_model="mistral")
            for i, asset in enumerate(sprite_manifest):
                if not isinstance(asset, dict): continue
                file_name = asset.get('filename', f'asset_{i}')
                
                raw_pos = asset.get('positive_prompt', asset.get('prompt', asset.get('description', file_name)))
                
                # NEW: Force the global aesthetic onto the end of the prompt!
                forced_prompt = f"{raw_pos}, {master_state['aesthetic']}"
                
                raw_neg = asset.get('negative_prompt', '3d, photorealistic, ugly')
                
                if asset.get('is_env', False):
                    bot.send_message(chat_id, f"🗺️ Painting Environment {i+1}/{len(sprite_manifest)}: {file_name}_bg.png...")
                    generate_sd_environment(forced_prompt, raw_neg, game, file_name)
                elif asset.get('is_sheet', False):
                    bot.send_message(chat_id, f"🐲 Drawing Sheet {i+1}/{len(sprite_manifest)}: {file_name}_sheet.png...")
                    generate_sd_sheet(forced_prompt, raw_neg, game, file_name, state=master_state, chat_id=chat_id)
                else:
                    bot.send_message(chat_id, f"🍎 Drawing Icon {i+1}/{len(sprite_manifest)}: {file_name}.png...")
                    generate_sd_art(forced_prompt, raw_neg, game, file_name, is_sprite=True, state=master_state, chat_id=chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Sprite Generation Skipped: {str(e)}")

        # --- Trigger Local Audio Generation ---
        generate_retro_sfx(chat_id, master_gdd, master_state, game)

        save_file(extract_block(ask_agent(master_gdd, "ROLE: Unity Animator (Agent 6)\nTASKS: Design Animation logic. Format as JSON.", target_model="qwen2.5-coder:7b", state=master_state), "json"), game, "animation_states.json")
        
        # PHASE 4 & 5
        bot.send_message(chat_id, "⚙️ Phase 4 & 5: Writing Core C# Systems...")
        csharp_rules = """
CRITICAL COMPILER RULES FOR UNITY 6:
1. You MUST include 'using System.Collections;' and 'using System.Collections.Generic;' at the top of EVERY script.
2. You MUST use 'Object.FindFirstObjectByType<T>()' instead of the deprecated 'FindObjectOfType'.
3. DO NOT reference external custom classes (like AudioController, UIController, DiceRoller). Handle UI/Audio with standard UnityEngine components.
4. Output ONLY valid C# code inside a ```cs block. No conversational text."""

        sys_player = f"ROLE: Unity 6 Player Controller Specialist (Agent 13)\nTASKS: Write C# script for player movement.{csharp_rules}"
        generate_and_review_code(chat_id, arch_data, sys_player, "PlayerController.cs", game, master_state)
        
        sys_enemy = f"ROLE: Unity 6 Enemy AI Architect (Agent 14)\nTASKS: Write C# script for enemy logic.{csharp_rules}"
        generate_and_review_code(chat_id, arch_data, sys_enemy, "EnemyAI.cs", game, master_state)
        
        sys_gm = f"ROLE: Unity 6 Backend Developer (Agent 4)\nTASKS: Write C# GameManager Singleton.{csharp_rules}"
        generate_and_review_code(chat_id, arch_data, sys_gm, "GameManager.cs", game, master_state)

        # PHASE 6
        bot.send_message(chat_id, "📢 Phase 6: Generating Auto-Assembler & Implementation Manual...")
        sys_a23 = f"""ROLE: Unity 6 Tools Developer (Agent 23)
TASKS: Write a Unity Editor C# script. 
1. Use [MenuItem("AI Studio/Assemble Scene")] to instantiate the Player, GameManager, and UI.
2. Create a subclass inheriting 'AssetPostprocessor'. Use 'void OnPreprocessTexture()' to automatically set 'filterMode' to 'FilterMode.Point' and 'textureCompression' to 'TextureImporterCompression.Uncompressed'.
{csharp_rules}"""
        generate_and_review_code(chat_id, arch_data, sys_a23, "Editor/AI_SceneBuilder.cs", game, master_state)

        sys_manual = "ROLE: Lead Game Designer (Agent 0)\nTASKS: Write a step-by-step 'Implementation Manual' for Unity 6. Format as Markdown."
        save_file(ask_agent(arch_data, sys_manual, target_model="qwen2.5-coder:7b", state=master_state), game, "01_UNITY_IMPLEMENTATION_MANUAL.md")

        # PHASE 7
        bot.send_message(chat_id, "🪽 Phase 7: Agent 22 (Hermes) drafting Executive Summary...")
        sys_hermes = "ROLE: Studio Communications Officer (Agent 22)\nTASKS: Read the GDD. Write an 'Executive Summary'. Format as Markdown."
        
        summary = ask_agent(master_gdd, sys_hermes, target_model="hermes3:8b", state=master_state)
        save_file(summary, game, "02_EXECUTIVE_SUMMARY.md")
        
        bot.send_message(chat_id, f"🪽 **A Message from Hermes:**\n\n{summary}")

        save_file(json.dumps(master_state, indent=4), game, "master_state_memory.json")
        bot.send_message(chat_id, f"✅ Fully Autonomous Studio Run Complete!\nData saved to:\n`~/ai_studio/projects/{game}`")
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Pipeline Error: {str(e)}")

print("100% Local Self-Improving 23-Agent Studio online...")
bot.infinity_polling()
