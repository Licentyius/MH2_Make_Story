#############################################################################
##
## Make_story- a plugin for makehuman 2 to create a backstory for characters V1.2
## Part of the MakeHuman 2 Project contributed by Elvaerwyn_MH2 2026
##
#############################################################################

import os
import json
import random
from PySide6 import QtWidgets, QtCore

TOOL_NAME = "Character Profile & Story"

global _story_last_seen_human_id
global _story_ui_memory_cache
global _story_background_poll_timer
global _active_story_window

_story_last_seen_human_id = None
_story_ui_memory_cache = {}
_story_background_poll_timer = None
_active_story_window = None

# --- Automated Functions ---
def calculate_zodiac(month, day):
    zodiac_signs = [
        (1, 20, "Capricorn"), (2, 19, "Aquarius"), (3, 21, "Pisces"),
        (4, 20, "Aries"), (5, 21, "Taurus"), (6, 21, "Gemini"),
        (7, 23, "Cancer"), (8, 23, "Leo"), (9, 23, "Virgo"),
        (10, 23, "Libra"), (11, 22, "Scorpio"), (12, 22, "Sagittarius")
    ]
    for m, d, sign in zodiac_signs:
        if month == m and day < d:
            return sign
    if month == 12 and day >= 22:
        return "Capricorn"
    for m, d, sign in zodiac_signs:
        if month == m:
            idx = zodiac_signs.index((m, d, sign))
            return zodiac_signs[(idx + 1) % 12]
    return "Unknown"

def determine_historical_era(year):
    if year < 500: 
        return f"{abs(year)} BCE" if year < 0 else "Classical Antiquity (Ancient Rome/Greece)"
    elif year < 1500: 
        return "Middle Ages (Medieval Era)"
    elif year < 1800: 
        return "Early Modern Period (Renaissance/Age of Sail)"
    elif year < 1900: 
        return "Victorian / Industrial Era"
    elif year < 2000: 
        return "Late 20th Century (Modern History)"
    elif year < 2030: 
        return "Contemporary / Information Age"
    elif year < 2100: 
        return "Near Future / Speculative Cyberpunk Era"
    else: 
        return "Far Future / Spacefaring Sci-Fi Era"

def load_extension(app, glob_reference=None):
    """
    Unified Non-Parallel Entry Point. 
    Builds the UI canvas, hooks up interactions, and displays the panel safely.
    """
    global _active_story_window, _story_background_poll_timer
    print("[Story Core] Spawning clean Character Profile interface frame...")

    try:
        _active_story_window = QtWidgets.QWidget()
        _active_story_window.setWindowTitle("Character Profile & Story")
        _active_story_window.resize(600, 520)
        
        master_layout = QtWidgets.QVBoxLayout(_active_story_window)
        master_layout.setContentsMargins(10, 10, 10, 10)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_content_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_content_layout.setSpacing(12)
        scroll.setWidget(scroll_content)
        master_layout.addWidget(scroll)

        # --- TOP LEVEL ACTION ROW ---
        group_actions = QtWidgets.QGroupBox("Quick Actions")
        layout_actions = QtWidgets.QHBoxLayout(group_actions)
        
        random_btn = QtWidgets.QPushButton("🎲 Randomize Traits")
        layout_actions.addWidget(random_btn)
        
        bio_btn = QtWidgets.QPushButton("✍️ Generate Bio Paragraph")
        layout_actions.addWidget(bio_btn)
        scroll_content_layout.addWidget(group_actions)

        # =======================================================================
        # SECTION 1: CORE IDENTITY & CALCULATORS
        # =======================================================================

        group_identity = QtWidgets.QGroupBox("Core Identity")
        layout_identity = QtWidgets.QVBoxLayout(group_identity)
        
        layout_identity.addWidget(QtWidgets.QLabel("Character Name:"))
        name_field = QtWidgets.QLineEdit()
        name_field.setPlaceholderText("Enter full name...")
        layout_identity.addWidget(name_field)

        layout_identity.addWidget(QtWidgets.QLabel("Date of Birth (YYYY-MM-DD or MM-DD):"))
        dob_field = QtWidgets.QLineEdit()
        dob_field.setPlaceholderText("e.g., 1987-05-04")
        layout_identity.addWidget(dob_field)

        zodiac_label = QtWidgets.QLabel("<b>Zodiac Sign:</b> <i>Enter a valid date...</i>")
        layout_identity.addWidget(zodiac_label)
        
        era_label = QtWidgets.QLabel("<b>Historical Placement:</b> <i>Enter a year...</i>")
        layout_identity.addWidget(era_label)
        scroll_content_layout.addWidget(group_identity)

        # =======================================================================
        # SECTION 2: BACKGROUND & BELIEFS
        # =======================================================================

        group_beliefs = QtWidgets.QGroupBox("Societal & Personal Background")
        layout_beliefs = QtWidgets.QVBoxLayout(group_beliefs)

        layout_beliefs.addWidget(QtWidgets.QLabel("Career / Occupation:"))
        career_field = QtWidgets.QLineEdit()
        career_field.setPlaceholderText("e.g., Real-Life Santa, Dog Walker")
        layout_beliefs.addWidget(career_field)

        layout_beliefs.addWidget(QtWidgets.QLabel("Political Affiliation / Faction:"))
        politics_field = QtWidgets.QLineEdit()
        politics_field.setPlaceholderText("e.g., Green Party, Rebel Alliance")
        layout_beliefs.addWidget(politics_field)

        layout_beliefs.addWidget(QtWidgets.QLabel("Religion / Belief System:"))
        religion_field = QtWidgets.QLineEdit()
        religion_field.setPlaceholderText("e.g., I believe in nothing, Praise the Sun")
        layout_beliefs.addWidget(religion_field)

        layout_beliefs.addWidget(QtWidgets.QLabel("Moral Alignment:"))
        alignment_field = QtWidgets.QComboBox()
        alignment_field.addItems(["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"])
        alignment_field.setCurrentIndex(4)
        layout_beliefs.addWidget(alignment_field)

        scroll_content_layout.addWidget(group_beliefs)

        # =======================================================================
        # SECTION 3: ATTRIBUTES, TRAITS & SKILLS
        # =======================================================================

        group_traits = QtWidgets.QGroupBox("Traits & Characteristics")
        layout_traits = QtWidgets.QVBoxLayout(group_traits)

        layout_traits.addWidget(QtWidgets.QLabel("Personality Traits (Comma Separated):"))
        traits_field = QtWidgets.QLineEdit()
        traits_field.setPlaceholderText("e.g., Bored, Stoic, Highly festive")
        layout_traits.addWidget(traits_field)

        layout_traits.addWidget(QtWidgets.QLabel("Social Skills & Demeanour:"))
        social_field = QtWidgets.QComboBox()
        social_field.addItems(["Unspecified", "Charismatic Diplomat", "Awkward Introvert", "Intimidating / Aggressive", "Charming Rogue", "Reserved Scholar", "Woeful Wallflower", "Perfectly Pragmatic", "Agressive Jock"])
        layout_traits.addWidget(social_field)

        layout_traits.addWidget(QtWidgets.QLabel("Physicality & Build Notes:"))
        physical_field = QtWidgets.QLineEdit()
        physical_field.setPlaceholderText("e.g., 6 foot 9 colossal frame, Butter butt, Waif-like")
        layout_traits.addWidget(physical_field)

        layout_traits.addWidget(QtWidgets.QLabel("Hobbies & Pastimes:"))
        hobbies_field = QtWidgets.QLineEdit()
        hobbies_field.setPlaceholderText("e.g., Weightlifter, Alchemy, Toy making, Falconer,")
        layout_traits.addWidget(hobbies_field)

        layout_traits.addWidget(QtWidgets.QLabel("Lifestyle Description:"))
        lifestyle_field = QtWidgets.QComboBox()
        lifestyle_field.addItems(["Unspecified", "Ascetic / Minimalist", "Luxurious / Noble", "Nomadic / Wanderer", "Urban / Working Class", "Rustic / Rural Homestead", "Off-grid / Hoarder", "Basement Dweller / Shut In"])
        layout_traits.addWidget(lifestyle_field)

        scroll_content_layout.addWidget(group_traits)

        # =======================================================================
        # SECTION 4: PREFERENCES & FANTASY ARCHETYPES
        # =======================================================================

        group_fantasy = QtWidgets.QGroupBox("Preferences & Fantasy Counterpart")
        layout_fantasy = QtWidgets.QVBoxLayout(group_fantasy)

        layout_fantasy.addWidget(QtWidgets.QLabel("Fantasy Race / Counterpart Class:"))
        fantasy_field = QtWidgets.QComboBox()
        fantasy_field.addItems(["Standard Human", "High Elf Mage", "Dwarven Berserker", "Cybernetic Android (mh2bot)", "Orcish Shaman", "Tiefling Rogue", "Celestial Paladin", "Earthen Juggernaut", "Alien LLama Herder"])
        layout_fantasy.addWidget(fantasy_field)

        layout_fantasy.addWidget(QtWidgets.QLabel("Favorite Color:"))
        color_field = QtWidgets.QLineEdit()
        color_field.setPlaceholderText("e.g., Crimson Red, Brown")
        layout_fantasy.addWidget(color_field)

        layout_fantasy.addWidget(QtWidgets.QLabel("Favorite Food / Cuisine:"))
        food_field = QtWidgets.QLineEdit()
        food_field.setPlaceholderText("e.g., Mead, Sushi, Hearty Stew, Bannok, Nordic Fish, Red Berries, Green Algea, Tacos, Steak & Eggs, Island Breeze Slaw, Reindeer Jerky")
        layout_fantasy.addWidget(food_field)

        layout_fantasy.addWidget(QtWidgets.QLabel("Music Genre Preference:"))
        music_field = QtWidgets.QComboBox()
        music_field.addItems(["Unspecified", "Classical / Orchestral", "Fantasy Bardic Folk", "Synthwave / Cyberpunk", "Rock / Metal", "Pop / Modern", "Jazz / Blues", "Ambient / Drone", "Zef / Fweeky", "Punk", "Grunge", "Country / Western"])
        layout_fantasy.addWidget(music_field)

        scroll_content_layout.addWidget(group_fantasy)

        # =======================================================================
        # SECTION 5: PROFILE METADATA SAVE CONTROLS
        # =======================================================================

        group_save = QtWidgets.QGroupBox("Profile Actions")
        layout_save = QtWidgets.QVBoxLayout(group_save)

        layout_save.addWidget(QtWidgets.QLabel("Character Backstory & Profile Notes:"))
        story_field = QtWidgets.QPlainTextEdit()
        story_field.setPlaceholderText("Write detailed character biographies here...")
        layout_save.addWidget(story_field)

        embed_checkbox = QtWidgets.QCheckBox("Embed Profile as 3D Asset Metadata")
        embed_checkbox.setChecked(True)
        layout_save.addWidget(embed_checkbox)

        save_btn = QtWidgets.QPushButton("Force Bind Profile Data")
        layout_save.addWidget(save_btn)

        scroll_content_layout.addWidget(group_save)
        # --- Nested Functions ---
        def parse_dob_live():
            text = dob_field.text().strip()
            if not text:
                zodiac_label.setText("<b>Zodiac Sign:</b> <i>Enter a date...</i>")
                era_label.setText("<b>Historical Placement:</b> <i>Enter a year...</i>")
                return "Unknown", "Unknown"
            
            parts = text.split('-')
            month_val, day_val, year_val = None, None, None

            try:
                if len(parts) == 3:
                    year_val = int(parts[0])
                    month_val = int(parts[1])
                    day_val = int(parts[2])
                elif len(parts) == 2:
                    month_val = int(parts[0])
                    day_val = int(parts[1])
            except (ValueError, IndexError):
                pass

            local_zodiac_result = "Unknown"
            if month_val and day_val and 1 <= month_val <= 12 and 1 <= day_val <= 31:
                local_zodiac_result = calculate_zodiac(month_val, day_val)
                zodiac_label.setText(f"Zodiac Sign: {local_zodiac_result} 🌟")
            else:
                zodiac_label.setText("Zodiac Sign: Invalid layout (use MM-DD or YYYY-MM-DD)")

            era_placement = "Unknown"
            if year_val is not None:
                era_placement = determine_historical_era(year_val)
                era_label.setText(f"Historical Placement: {era_placement}")
            else:
                era_label.setText("Historical Placement: Requires Year (YYYY-MM-DD)")

            return str(local_zodiac_result), str(era_placement)

        def get_active_human():
            if app and hasattr(app, 'selectedHuman'):
                return app.selectedHuman
            elif app and hasattr(app, 'human'):
                return app.human
            return None

        def sync_data_to_human():
            z_sign_string, era_place = parse_dob_live()
            payload = {
                "name": name_field.text().strip(),
                "dob": dob_field.text().strip(),
                "zodiac": z_sign_string,
                "historical_era": era_place,
                "career": career_field.text().strip(),
                "politics": politics_field.text().strip(),
                "religion": religion_field.text().strip(),
                "alignment": alignment_field.currentText(),
                "traits": traits_field.text().strip(),
                "social_skills": social_field.currentText(),
                "physicality": physical_field.text().strip(),
                "hobbies": hobbies_field.text().strip(),
                "lifestyle": lifestyle_field.currentText(),
                "fantasy_counterpart": fantasy_field.currentText(),
                "favorite_color": color_field.text().strip(),
                "favorite_food": food_field.text().strip(),
                "favorite_music": music_field.currentText(),
                "story": story_field.toPlainText().strip(),
                "embed_metadata": embed_checkbox.isChecked()
            }
            global _story_ui_memory_cache
            _story_ui_memory_cache = payload

            human = get_active_human()
            if not human:
                return payload

            if not hasattr(human, 'profile_metadata'):
                human.profile_metadata = {}
            human.profile_metadata.update(payload)

            for target in ['export_data', 'settings', 'export_extensions', 'custom_properties']:
                if hasattr(human, target):
                    dct = getattr(human, target)
                    if isinstance(dct, dict):
                        dct['profile_metadata'] = payload
                    elif dct is None:
                        setattr(human, target, {'profile_metadata': payload})
            return payload

        def randomize_all_fields():
            names = ["Thorgar Stonebutt", "Gideon Cyberwalk", "Mildred the Vague", "Bob Greenstone", "Elena Moonsinger", "Cpt. Butterbutt", "Nicholas Claus", "Smoke Antwood", "Ash Pickles", "Ralf Von Alden", "Willam the Brave"]
            careers = ["Real-Life Santa Claus", "Dog Walker", "Meme Archivist", "Alchemist's Intern", "Starship Dishwasher", "Professional Napper", "Underground Turnip Dealer", "Yoga Instructor", "Puppetmaster", "Avante Garde Seamstress"]
            politics = ["Green Party", "Royalist Faction", "Anarcho-Monarchist", "The Council of Bread", "Rebel Alliance", "Completely Indifferent", "Stoners United Someday", "Those who shalt not be Named"]
            religions = ["I believe in nothing", "Praise the Sun ☀️", "Cult of the Sacred Turnip", "Agnostic", "Devoted to the RNG Gods", "Secular Scholar", "Nerds 4 eva"]
            traits = ["Bored, easily distracted", "Stoic, heavily caffeinated", "Highly festive and jolly", "Suspiciously energetic", "Anxiously analytical", "Aggressively polite", "Constantly on the verge of a nap", "Chaos incarnate, easily bribed", "Overly confident, deeply confused", "Dramatically secretive about mundane things", "Professionally unbothered", "Quietly plotting a minor inconvenience", "Enthusiastically unqualified", "Sarcastic, but only in whispers", "Reluctantly helpful", "Slightly paranoid about birds", "Hypnotized by shiny objects", "Accidentally intimidating", "Intensely dedicated to snacks", "Optimistic to a dangerous degree"]
            physicality = ["I have butter butt", "6 foot 9 colossal build", "Surprisingly aerodynamic", "Stout and unmovable", "Built like an iron anvil", "If I turn sideways I vanish", "Waif-Like", "Built"]
            hobbies = ["Weightlifter", "Lute tuning", "Toy making", "Alchemy", "Extreme sitting", "Hog riding", "Cat Herding", "Putting ships in Bottles", "Crocheting Chijuajuah Sweaters"]
            colors = ["Brown", "Crimson Red", "Cyberpunk Neon Pink", "Deep Void Black", "Forest Green", "Lembas Gold", "Periwinkle", "Brilliant Blue", "Makehuman Orange", "Black like my Soul", "Grey of course", "Violet"]
            foods = ["Mead", "Elven Lembas Bread", "Hearty Stew", "Cold Pizza", "Roasted Turnips", "Spicy Ramen", "Deep Fried Worms", "Eggs", "Rockey Mountain Oysters", "Pickled Carrots", "I only eat bread" ]
            stories = [
                "There is a story its noones buisness",
                "Left their home town because of a tragic turnip shortage.",
                "Woke up inside an automated cloning chamber with zero memory and a strong craving for Mead.",
                "Once fought a tavern mimic with nothing but a wooden ladle.",
                "Just trying to pay off their galactic student loans.",
                "Accidentally joined a cult while looking for the bathroom.",
                "Banned from three separate star systems for excessive aggressive whistling.",
                "Thinks they are a legendary wizard, but actually just throws very bright flashbangs.",
                "Traded their kingdom for a really good grilled cheese sandwich.",
                "On the run from a sentient, highly vengeful toaster.",
                "Possessed by a ghost that only communicates in terrible puns.",
                "Won their current spaceship in a high-stakes game of Rock, Paper, Scissors.",
                "Spoke to a river sprite once and now entirely refuses to wear shoes.",
                "Still waiting for a message from a carrier pigeon that left six years ago.",
                "Accidentally duplicated themselves and now works as their own twin brother.",
                "Left their home planet because the local elevator music was driving them mad.",
                "Once convinced an entire goblin tribe that they were a minor deity of laundry.",
                "Currently pretending to know how to fly this ship until someone notices.",
                "Chose this life because a magic eight-ball told them to.",
                "Seeking revenge on the tailor who gave them these itchy trousers."
            ]

            rand_year = random.randint(1000, 2150)
            rand_month = random.randint(1, 12)
            rand_day = random.randint(1, 28)
            rand_dob = f"{rand_year:04d}-{rand_month:02d}-{rand_day:02d}"

            name_field.setText(random.choice(names))
            dob_field.setText(rand_dob)
            career_field.setText(random.choice(careers))
            politics_field.setText(random.choice(politics))
            religion_field.setText(random.choice(religions))
            traits_field.setText(random.choice(traits))
            physical_field.setText(random.choice(physicality))
            hobbies_field.setText(random.choice(hobbies))
            color_field.setText(random.choice(colors))
            food_field.setText(random.choice(foods))
            story_field.setPlainText(random.choice(stories))

            for combo in [alignment_field, social_field, lifestyle_field, fantasy_field, music_field]:
                rand_index = random.randint(0, combo.count() - 1)
                combo.setCurrentIndex(rand_index)

            parse_dob_live()
            sync_data_to_human()

        def generate_story_paragraph():
            data = sync_data_to_human()
            if not data or not data["name"]:
                QtWidgets.QMessageBox.warning(None, "Name Missing", "Please enter a character name first.")
                return

            name = data["name"]
            career = data["career"] if data["career"] else "Wanderer"
            alignment = data["alignment"]
            traits = data["traits"] if data["traits"] else "mysterious"
            physicality = data["physicality"] if data["physicality"] else "unique frame"
            hobbies = data["hobbies"] if data["hobbies"] else "adventuring"
            fantasy = data["fantasy_counterpart"]
            color = data["favorite_color"] if data["favorite_color"] else "unknown hues"
            food = data["favorite_food"] if data["favorite_food"] else "rations"
            music = data["favorite_music"]
            
            bio_paragraph = (
                f"Known across the realm as a {alignment} {fantasy}, {name} cuts an imposing figure, "
                f"frequently described as having a {physicality}. Professionally operating as a {career}, "
                f"they are often considered quite {traits} by those who cross their path.\n\n"
                f"When not occupied with the demands of their trade, they can be found indulging in "
                f"their favorite pastime of {hobbies}. They possess a strong affinity for the color {color}, "
                f"and have a well-known weakness for {food}—ideally enjoyed while listening to the soothing "
                f"sounds of {music} echoes in the background."
            )
            
            story_field.setPlainText(bio_paragraph)
            sync_data_to_human()

        def refresh_ui_safely():
            human = get_active_human()
            if not human: 
                return

            current_id = id(human)
            global _story_last_seen_human_id, _story_ui_memory_cache
            if _story_last_seen_human_id == current_id:
                if not hasattr(human, 'profile_metadata') and _story_ui_memory_cache:
                    human.profile_metadata = _story_ui_memory_cache.copy()
                return

            data = getattr(human, 'profile_metadata', {})
            if not data and hasattr(human, 'settings') and isinstance(human.settings, dict):
                data = human.settings.get('profile_metadata', {})

            if data:
                for widget in [name_field, dob_field, career_field, politics_field, religion_field, 
                               alignment_field, traits_field, social_field, physical_field, 
                               hobbies_field, lifestyle_field, fantasy_field, color_field, 
                               food_field, music_field, story_field, embed_checkbox]:
                    widget.blockSignals(True)

                name_field.setText(data.get("name", ""))
                dob_field.setText(data.get("dob", ""))
                career_field.setText(data.get("career", ""))
                politics_field.setText(data.get("politics", ""))
                religion_field.setText(data.get("religion", ""))
                traits_field.setText(data.get("traits", ""))
                physical_field.setText(data.get("physicality", ""))
                hobbies_field.setText(data.get("hobbies", ""))
                color_field.setText(data.get("favorite_color", ""))
                food_field.setText(data.get("favorite_food", ""))
                story_field.setPlainText(data.get("story", ""))
                embed_checkbox.setChecked(data.get("embed_metadata", True))

                for field, key, default in [
                    (alignment_field, "alignment", "True Neutral"),
                    (social_field, "social_skills", "Unspecified"),
                    (lifestyle_field, "lifestyle", "Unspecified"),
                    (fantasy_field, "fantasy_counterpart", "Standard Human"),
                    (music_field, "favorite_music", "Unspecified")
                ]:
                    idx = field.findText(data.get(key, default))
                    if idx >= 0:
                        field.setCurrentIndex(idx)

                for widget in [name_field, dob_field, career_field, politics_field, religion_field, 
                               alignment_field, traits_field, social_field, physical_field, 
                               hobbies_field, lifestyle_field, fantasy_field, color_field, 
                               food_field, music_field, story_field, embed_checkbox]:
                    widget.blockSignals(False)
                
                parse_dob_live()

            _story_last_seen_human_id = current_id

        def force_manual_save_out():
            data = sync_data_to_human()
            if not data or not data["name"]:
                QtWidgets.QMessageBox.warning(None, "Empty Data", "Please fill out at least a Character Name to bind.")
                return

            export_dir = None
            if app and hasattr(app, 'getPath'):
                try: export_dir = app.getPath('exports')
                except Exception: pass

            if not export_dir:
                export_dir = os.path.expanduser("~/.makehuman2/exports")

            try:
                os.makedirs(export_dir, exist_ok=True)
                safe_filename = "".join([c for c in data["name"] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                out_path = os.path.join(export_dir, f"{safe_filename}_fleshed_profile.json")
                
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                    
                print(f"[Story Extension] Profile written successfully: {out_path}")
                QtWidgets.QMessageBox.information(None, "Success!", f"Character profile safely bound and saved to:\n{out_path}")
            except Exception as e:
                print(f"Write failure: {e}")

        # --- Live Signals Connection ---
        name_field.textChanged.connect(sync_data_to_human)
        dob_field.textChanged.connect(sync_data_to_human)
        career_field.textChanged.connect(sync_data_to_human)
        politics_field.textChanged.connect(sync_data_to_human)
        religion_field.textChanged.connect(sync_data_to_human)
        traits_field.textChanged.connect(sync_data_to_human)
        physical_field.textChanged.connect(sync_data_to_human)
        hobbies_field.textChanged.connect(sync_data_to_human)
        color_field.textChanged.connect(sync_data_to_human)
        food_field.textChanged.connect(sync_data_to_human)
        story_field.textChanged.connect(sync_data_to_human)
        
        alignment_field.currentIndexChanged.connect(sync_data_to_human)
        social_field.currentIndexChanged.connect(sync_data_to_human)
        lifestyle_field.currentIndexChanged.connect(sync_data_to_human)
        fantasy_field.currentIndexChanged.connect(sync_data_to_human)
        music_field.currentIndexChanged.connect(sync_data_to_human)
        embed_checkbox.stateChanged.connect(sync_data_to_human)
        dob_field.textChanged.connect(lambda: parse_dob_live())
        
        random_btn.clicked.connect(randomize_all_fields)
        bio_btn.clicked.connect(generate_story_paragraph)
        save_btn.clicked.connect(force_manual_save_out)

        # Initialize tracking clock loop
        _story_background_poll_timer = QtCore.QTimer()
        _story_background_poll_timer.timeout.connect(refresh_ui_safely)
        _story_background_poll_timer.start(500)
        
        refresh_ui_safely()
        
        # 1. Wrap the active window panel into a native PySide6 Dock container
        dock_container = QtWidgets.QDockWidget("Character Profile & Story", app)
        dock_container.setWidget(_active_story_window)
        
        # Set a modern, comfortable width 
        dock_container.setMinimumWidth(350)
        
        # Give the dock closeable and movable features natively.
        # This allows it to collapse and untrack cleanly from the workspace.
        dock_container.setFeatures(QtWidgets.QDockWidget.DockWidgetClosable | QtWidgets.QDockWidget.DockWidgetMovable)
        
        # 2. Dock it cleanly into the native left sidebar layout area of the main window
        app.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_container)
        
        print("[Story Core Success] Character Profile panel safely docked and formatted!")
        return _active_story_window

    except Exception as err:
        import traceback
        print(f"[Story Core Fatal] Execution block crashed during instantiation: {err}")
        traceback.print_exc()
        return None


def unload_extension():
    """Safely closes the standalone window and frees up system memory blocks."""
    global _active_story_window, _story_background_poll_timer
    print("[Story Core] Cleaning memory nodes out of thread stream...")
    if _story_background_poll_timer is not None:
        _story_background_poll_timer.stop()
    if _active_story_window is not None:
        try:
            _active_story_window.close()
            _active_story_window.deleteLater()
        except Exception:
            pass
    _active_story_window = None
