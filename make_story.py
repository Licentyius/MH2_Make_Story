#############################################################################
##
## Make_story- a plugin for makehuman 2 to create a backstory for characters V1.3
## Part of the MakeHuman 2 Project contributed by Elvaerwyn_MH2 2026
##
#############################################################################

import os
import json
import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QWidget, QApplication, QMainWindow, QMessageBox,
       QVBoxLayout, QDockWidget, QScrollArea, QFrame, QGroupBox, QHBoxLayout,
       QPushButton, QFormLayout, QLineEdit, QLabel, QComboBox, QPlainTextEdit,
       QCheckBox)

class MakeStoryPanel(QWidget):
    def __init__(self,  app_reference, glob_reference, pluginname):
        self.glob = glob_reference
        self.main_window = self.glob.MainWindow
        self.mh_app = app_reference
        self.pluginname = pluginname
        super().__init__(self.glob.MainWindow)
        self.repo = self.glob.pluginRepo
        self.dock = None
        self.panel = None
        self.story_background_poll_timer = None
        self.story_ui_memory_cache = {}
        self.story_last_seen_human_id = None
        self.profiles = {}

    def calculate_zodiac(self, month, day):
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
                next_sign_tuple = zodiac_signs[(idx + 1) % 12]
                return next_sign_tuple[2]
        return "Unknown"

    def determine_historical_era(self, year):
        if year < 500: return f"{abs(year)} BCE" if year < 0 else "Classical Antiquity (Ancient Rome/Greece)"
        elif year < 1500: return "Middle Ages (Medieval Era)"
        elif year < 1800: return "Early Modern Period (Renaissance/Age of Sail)"
        elif year < 1900: return "Victorian / Industrial Era"
        elif year < 2000: return "Late 20th Century (Modern History)"
        elif year < 2030: return "Contemporary / Information Age"
        elif year < 2100: return "Near Future / Speculative Cyberpunk Era"
        else: return "Far Future / Spacefaring Sci-Fi Era"

    def parse_dob_live(self):
        panel = self.panel
        text = panel.dob_field.text().strip()
        if not text:
            panel.zodiac_label.setText("<b>Zodiac Sign:</b> <i>Enter a date...</i>")
            panel.era_label.setText("<b>Historical Placement:</b> <i>Enter a year...</i>")
            return "Unknown", "Unknown"
        parts = text.split('-')
        month_val, day_val, year_val = None, None, None
        try:
            if len(parts) == 3:
                year_val, month_val, day_val = int(parts[0]), int(parts[1]), int(parts[2])
            elif len(parts) == 2:
                month_val, day_val = int(parts[0]), int(parts[1])
        except (ValueError, IndexError): pass

        local_zodiac_result = "Unknown"
        if month_val and day_val and 1 <= month_val <= 12 and 1 <= day_val <= 31:
            local_zodiac_result = self.calculate_zodiac(month_val, day_val)
            panel.zodiac_label.setText(f"Zodiac Sign: {local_zodiac_result} 🌟")
        else:
            panel.zodiac_label.setText("Zodiac Sign: Invalid layout (use MM-DD or YYYY-MM-DD)")

        era_placement = "Unknown"
        if year_val is not None:
            era_placement = self.determine_historical_era(year_val)
            panel.era_label.setText(f"Historical Placement: {era_placement}")
        else:
            panel.era_label.setText("Historical Placement: Requires Year (YYYY-MM-DD)")
        return str(local_zodiac_result), str(era_placement)

    def get_active_human(self):
        """
        only information we have is the active selected human, which can be used as a key to own dictionary
        """
        return self.glob.baseClass.name

    def sync_data_to_human(self):
        panel = self.panel
        z_sign_string, era_place = self.parse_dob_live()
        payload = {
            "name": panel.name_field.text().strip(), "dob": panel.dob_field.text().strip(), "zodiac": z_sign_string,
            "historical_era": era_place, "career": panel.career_field.text().strip(), "politics": panel.politics_field.text().strip(),
            "religion": panel.religion_field.text().strip(), "alignment": panel.alignment_field.currentText(),
            "traits": panel.traits_field.text().strip(), "social_skills": panel.social_field.currentText(),
            "physicality": panel.physical_field.text().strip(), "hobbies": panel.hobbies_field.text().strip(),
            "lifestyle": panel.lifestyle_field.currentText(), "fantasy_counterpart": panel.fantasy_field.currentText(),
            "favorite_color": panel.color_field.text().strip(), "favorite_food": panel.food_field.text().strip(),
            "favorite_music": panel.music_field.currentText(), "story": panel.story_field.toPlainText().strip(),
            "embed_metadata": panel.embed_checkbox.isChecked()
        }
        self.story_ui_memory_cache = payload
        human = self.get_active_human()
        if human in self.profiles:
            self.profiles[human].update(payload)
        else:
            self.profiles[human] = payload
        return payload

    def randomize_all_fields(self):
        panel = self.panel
        names = ["Thorgar Stonebutt", "Gideon Cyberwalk", "Mildred the Vague", "Bob Greenstone", "Elena Moonsinger", "Cpt. Butterbutt", "Nicholas Claus", "Smoke Antwood", "Ash Pickles", "Ralf Von Alden", "Willam the Brave", "Lady Grey", "Joel the Explorer", "Sir Joe", "Roachman", "Raider da Pirate Hunta", "Wyndia Drayton", "Margaret the Staunch"]
        careers = ["Real-Life Santa Claus", "Dog Walker", "Meme Archivist", "Alchemist's Intern", "Starship Dishwasher", "Professional Napper", "Underground Turnip Dealer", "Yoga Instructor", "Puppetmaster", "Avante Garde Seamstress", "Librarian", "Street Taco Vender"]
        politics = ["Green Party", "Royalist Faction", "Anarcho-Monarchist", "The Council of Bread", "Rebel Alliance", "Completely Indifferent", "Stoners United Someday", "Those who shalt not be Named"]
        religions = ["I believe in nothing()", "Praise the Sun ☀️", "Cult of the Sacred Turnip 🫜", "Agnostic", "Devoted to the RNG Gods 🎲", "Secular Scholar 🎓", "Nerds 4 eva 🤓", "Science is my Religion ⚛️", "I believe in Magical Thinking 🔮"]
        traits = ["Bored, easily distracted", "Stoic, heavily caffeinated", "Highly festive and jolly", "Suspiciously energetic ⚡", "Anxiously analytical", "Aggressively polite", "Constantly on the verge of a nap", "Chaos incarnate, easily bribed", "Overly confident, deeply confused", "Dramatically secretive about mundane things", "Professionally unbothered", "Quietly plotting a minor inconvenience", "Enthusiastically unqualified", "Sarcastic, but only in whispers", "Reluctantly helpful", "Slightly paranoid about birds", "Hypnotized by shiny objects", "Accidentally intimidating", "Intensely dedicated to snacks", "Optimistic to a dangerous degree", "Burning the candle from both ends 🕯️"]
        physicality = ["I have butter butt", "6 foot 9 colossal build", "Surprisingly aerodynamic", "Stout and unmovable", "Built like an iron anvil", "If I turn sideways I vanish", "Waif-Like", "Built"]
        hobbies = ["Weightlifter", "Lute tuning", "Toy making", "Alchemy", "Extreme sitting", "Hog riding", "Cat Herding", "Putting ships in Bottles", "Crocheting Chijuajuah Sweaters"]
        colors = ["Brown", "Crimson Red", "Cyberpunk Neon Pink", "Deep Void Black", "Forest Green", "Lembas Gold", "Periwinkle", "Brilliant Blue", "Makehuman Orange", "Black like my Soul", "Grey of course", "Violet"]
        foods = ["Mead", "Elven Lembas Bread", "Hearty Stew", "Cold Pizza", "Roasted Turnips", "Spicy Ramen", "Deep Fried Worms", "Eggs", "Rockey Mountain Oysters", "Pickled Carrots", "I only eat bread"]
        stories = ["There is a story its noones buisness", "Left their home town because of a tragic turnip shortage.", "Woke up inside an automated cloning chamber with zero memory.", "Once fought a tavern mimic with nothing but a wooden ladle.", "Just trying to pay off their galactic student loans.", "Accidentally joined a cult while looking for the bathroom.", "Banned from three separate star systems.", "Thinks they are a legendary wizard.", "Traded their kingdom for a grilled cheese sandwich.", "On the run from a sentient toaster.", "Possessed by a ghost that speaks in puns.", "Won their space ship in Rock, Paper, Scissors.", "Refuses to wear shoes.", "Waiting for a carrier pigeon.", "Accidentally duplicated themselves.", "Laundry deity."]

        rand_year, rand_month, rand_day = random.randint(1000, 2150), random.randint(1, 12), random.randint(1, 28)
        panel.name_field.setText(random.choice(names))
        panel.dob_field.setText(f"{rand_year:04d}-{rand_month:02d}-{rand_day:02d}")
        panel.career_field.setText(random.choice(careers))
        panel.politics_field.setText(random.choice(politics))
        panel.religion_field.setText(random.choice(religions))
        panel.traits_field.setText(random.choice(traits))
        panel.physical_field.setText(random.choice(physicality))
        panel.hobbies_field.setText(random.choice(hobbies))
        panel.color_field.setText(random.choice(colors))
        panel.food_field.setText(random.choice(foods))
        panel.story_field.setPlainText(random.choice(stories))
        for combo in [panel.alignment_field, panel.social_field, panel.lifestyle_field, panel.fantasy_field, panel.music_field]:
            combo.setCurrentIndex(random.randint(0, combo.count() - 1))
        self.parse_dob_live()
        self.sync_data_to_human()

    def generate_story_paragraph(self):
        data = self.sync_data_to_human()
        if not data or not data["name"]:
            QMessageBox.warning(None, "Name Missing", "Please enter a character name or randomize it first.")
            return

        name = data["name"]
        career = data["career"] if data["career"] else "Wanderer"
        alignment = data["alignment"]
        traits = data["traits"] if data["traits"] else "mysterious"
        physicality = data["physicality"] if data["physicality"] else "unique frame"
        hobbies = data["hobbies"] if data["hobbies"] else "adventuring"

        fantasy = data["fantasy_counterpart"] if data["fantasy_counterpart"] else "Standard Human"
    
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
    
        self.panel.story_field.setPlainText(bio_paragraph)
        self.sync_data_to_human()

    def refresh_ui_safely(self):
        panel = self.panel

        human = self.get_active_human()
        if not human:
            return

        if self.story_last_seen_human_id == human:
            return

        # check if we have the data already inside memory, if so set values (this happens when character is
        # loaded again in same session
        #
        data = self.profiles[human] if human in self.profiles else None

        if data:
            widgets = [panel.name_field, panel.dob_field, panel.career_field, panel.politics_field, panel.religion_field, panel.alignment_field, panel.traits_field, panel.social_field, panel.physical_field, panel.hobbies_field, panel.lifestyle_field, panel.fantasy_field, panel.color_field, panel.food_field, panel.music_field, panel.story_field, panel.embed_checkbox]
            for w in widgets:
                w.blockSignals(True)
            
            panel.name_field.setText(data.get("name", ""))
            panel.dob_field.setText(data.get("dob", ""))
            panel.career_field.setText(data.get("career", ""))
            panel.politics_field.setText(data.get("politics", ""))
            panel.religion_field.setText(data.get("religion", ""))
            panel.traits_field.setText(data.get("traits", ""))
            panel.physical_field.setText(data.get("physicality", ""))
            panel.hobbies_field.setText(data.get("hobbies", ""))
            panel.color_field.setText(data.get("favorite_color", ""))
            panel.food_field.setText(data.get("favorite_food", ""))
            panel.story_field.setPlainText(data.get("story", ""))
            panel.embed_checkbox.setChecked(data.get("embed_metadata", True))
        
            for field, key, default in [(panel.alignment_field, "alignment", "True Neutral"),
                    (panel.social_field, "social_skills", "Unspecified"),
                    (panel.lifestyle_field, "lifestyle", "Unspecified"),
                    (panel.fantasy_field, "fantasy_counterpart", "Standard Human"),
                    (panel.music_field, "favorite_music", "Unspecified")]:
                idx = field.findText(data.get(key, default))
                if idx >= 0:
                    field.setCurrentIndex(idx)
                
            for w in widgets:
                w.blockSignals(False)
            self.parse_dob_live()
        
        self.story_last_seen_human_id = human

    def force_manual_save_out(self):
        data = self.sync_data_to_human()
        if not data or not data["name"]:
            QMessageBox.warning(None, "Empty Data", "Please fill out or randomize a Character Name first.")
            return

        # export dir is generated when makehuman starts or a new basemesh is selected
        #
        export_dir = self.glob.env.stdUserPath("exports")

        safe_filename = "".join([c for c in data["name"] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        out_path = os.path.join(export_dir, f"{safe_filename}_fleshed_profile.json")
        
        with open(out_path, 'w', encoding='utf-8') as f: 
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        QMessageBox.information(
            None, 
            "Success!", 
            f"Character profile successfully saved to your active User Data folder:\n\n{out_path}"
        )

    class Panel(QWidget):
        def __init__(self, parent):
            super().__init__()

            self.parent = parent

            self.setMinimumWidth(380)
            master_layout = QVBoxLayout(self)
            master_layout.setContentsMargins(6, 6, 6, 6)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll_content = QWidget()
            scroll_content_layout = QVBoxLayout(scroll_content)
            scroll_content_layout.setSpacing(10)
            scroll_content_layout.setContentsMargins(4, 4, 4, 4)
            scroll.setWidget(scroll_content)
            master_layout.addWidget(scroll)

            group_actions = QGroupBox("Quick Actions")
            layout_actions = QHBoxLayout(group_actions)
            layout_actions.setContentsMargins(8, 10, 8, 8)
            random_btn = QPushButton("🎲 Randomize Traits")
            random_btn.setMinimumHeight(28)
            layout_actions.addWidget(random_btn)
            bio_btn = QPushButton("✍️ Generate Bio Paragraph")
            bio_btn.setMinimumHeight(28)
            layout_actions.addWidget(bio_btn)
            scroll_content_layout.addWidget(group_actions)

            group_identity = QGroupBox("Core Identity")
            layout_identity = QFormLayout(group_identity)
            layout_identity.setContentsMargins(8, 10, 8, 8)
            layout_identity.setSpacing(6)
            self.name_field = QLineEdit()
            self.name_field.setPlaceholderText("Enter full name...")
            layout_identity.addRow("Character Name:", self.name_field)
            self.dob_field = QLineEdit()
            self.dob_field.setPlaceholderText("e.g., 1987-05-04")
            layout_identity.addRow("Date of Birth:", self.dob_field)
            self.zodiac_label = QLabel("<i>Awaiting complete data...</i>")
            layout_identity.addRow("Zodiac Sign:", self.zodiac_label)
            self.era_label = QLabel("<i>Awaiting timeline year...</i>")
            layout_identity.addRow("Historical Era:", self.era_label)
            scroll_content_layout.addWidget(group_identity)

            group_beliefs = QGroupBox("Societal & Personal Background")
            layout_beliefs = QFormLayout(group_beliefs)
            layout_beliefs.setContentsMargins(8, 10, 8, 8)
            layout_beliefs.setSpacing(6)
            self.career_field = QLineEdit()
            self.career_field.setPlaceholderText("e.g., Real-Life Santa, Dog Walker")
            layout_beliefs.addRow("Occupation:", self.career_field)
            self.politics_field = QLineEdit()
            self.politics_field.setPlaceholderText("e.g., Green Party, Rebel Alliance")
            layout_beliefs.addRow("Faction/Politics:", self.politics_field)
            self.religion_field = QLineEdit()
            self.religion_field.setPlaceholderText("e.g., Praise the Sun ☀️")
            layout_beliefs.addRow("Belief System:", self.religion_field)
            self.alignment_field = QComboBox()
            self.alignment_field.addItems(["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"])
            self.alignment_field.setCurrentIndex(4)
            layout_beliefs.addRow("Moral Alignment:", self.alignment_field)
            scroll_content_layout.addWidget(group_beliefs)

            group_traits = QGroupBox("Traits & Characteristics")
            layout_traits = QFormLayout(group_traits)
            layout_traits.setContentsMargins(8, 10, 8, 8)
            layout_traits.setSpacing(6)
            self.traits_field = QLineEdit()
            self.traits_field.setPlaceholderText("e.g., Bored, Stoic, Highly festive")
            layout_traits.addRow("Behavioral Traits:", self.traits_field)
            self.social_field = QComboBox()
            self.social_field.addItems(["Unspecified", "Charismatic Diplomat", "Awkward Introvert", "Intimidating / Aggressive", "Charming Rogue", "Reserved Scholar", "Woeful Wallflower", "Perfectly Pragmatic", "Agressive Jock"])
            layout_traits.addRow("Social Demeanour:", self.social_field)
            self.physical_field = QLineEdit()
            self.physical_field.setPlaceholderText("Anatomical build notes...")
            layout_traits.addRow("Physicality Notes:", self.physical_field)
            self.hobbies_field = QLineEdit()
            self.hobbies_field.setPlaceholderText("e.g., Weightlifter, Alchemy, Falconer")
            layout_traits.addRow("Hobbies/Pastimes:", self.hobbies_field)
            self.lifestyle_field = QComboBox()
            self.lifestyle_field.addItems(["Unspecified", "Ascetic / Minimalist", "Luxurious / Noble", "Nomadic / Wanderer", "Urban / Working Class", "Rustic / Rural Homestead", "Off-grid / Hoarder", "Basement Dweller / Shut In"])
            layout_traits.addRow("Lifestyle Model:", self.lifestyle_field)
            scroll_content_layout.addWidget(group_traits)

            group_fantasy = QGroupBox("Preferences & Fantasy Counterpart")
            layout_fantasy = QFormLayout(group_fantasy)
            layout_fantasy.setContentsMargins(8, 10, 8, 8)
            layout_fantasy.setSpacing(6)
            self.fantasy_field = QComboBox()
            self.fantasy_field.addItems(["Standard Human", "High Elf Mage", "Dwarven Berserker", "Cybernetic Android (mh2bot)", "Orcish Shaman", "Tiefling Rogue", "Celestial Paladin", "Earthen Juggernaut", "Alien LLama Herder"])
            layout_fantasy.addRow("Class Construct:", self.fantasy_field)
            self.color_field = QLineEdit()
            self.color_field.setPlaceholderText("e.g., Crimson Red, Brown")
            layout_fantasy.addRow("Favorite Color:", self.color_field)
            self.food_field = QLineEdit()
            self.food_field.setPlaceholderText("Preferred organic fuel replenishment...")
            layout_fantasy.addRow("Favored Cuisine:", self.food_field)
            self.music_field = QComboBox()
            self.music_field.addItems(["Unspecified", "Classical / Orchestral", "Fantasy Bardic Folk", "Synthwave / Cyberpunk", "Rock / Metal", "Pop / Modern", "Jazz / Blues", "Ambient / Drone", "Zef / Fweeky", "Punk", "Grunge", "Country / Western"])
            layout_fantasy.addRow("Music Registry:", self.music_field)
            scroll_content_layout.addWidget(group_fantasy)

            group_save = QGroupBox("Profile Actions")
            layout_save = QVBoxLayout(group_save)
            layout_save.setContentsMargins(8, 10, 8, 8)
            layout_save.setSpacing(6)
            layout_save.addWidget(QLabel("Character Backstory Notes:"))
            self.story_field = QPlainTextEdit()
            self.story_field.setMinimumHeight(100)
            self.story_field.setPlaceholderText("Biographical outputs populate here...")
            layout_save.addWidget(self.story_field)
            self.embed_checkbox = QCheckBox("Embed Profile as 3D Asset Metadata")
            self.embed_checkbox.setChecked(True)
            layout_save.addWidget(self.embed_checkbox)
            self.save_btn = QPushButton("💾 Save Data And Bind to Active Character")
            self.save_btn.setMinimumHeight(30)
            layout_save.addWidget(self.save_btn)
            scroll_content_layout.addWidget(group_save)
            # Wire Up System Operations Matrix
            self.name_field.textChanged.connect(parent.sync_data_to_human)
            self.dob_field.textChanged.connect(parent.sync_data_to_human)
            self.career_field.textChanged.connect(parent.sync_data_to_human)
            self.politics_field.textChanged.connect(parent.sync_data_to_human)
            self.religion_field.textChanged.connect(parent.sync_data_to_human)
            self.traits_field.textChanged.connect(parent.sync_data_to_human)
            self.physical_field.textChanged.connect(parent.sync_data_to_human)
            self.hobbies_field.textChanged.connect(parent.sync_data_to_human)
            self.color_field.textChanged.connect(parent.sync_data_to_human)
            self.food_field.textChanged.connect(parent.sync_data_to_human)
            self.story_field.textChanged.connect(parent.sync_data_to_human)
            self.alignment_field.currentIndexChanged.connect(parent.sync_data_to_human)
            self.social_field.currentIndexChanged.connect(parent.sync_data_to_human)
            self.lifestyle_field.currentIndexChanged.connect(parent.sync_data_to_human)
            self.fantasy_field.currentIndexChanged.connect(parent.sync_data_to_human)
            self.music_field.currentIndexChanged.connect(parent.sync_data_to_human)
            self.embed_checkbox.stateChanged.connect(parent.sync_data_to_human)
            self.dob_field.textChanged.connect(lambda: parent.parse_dob_live())
            random_btn.clicked.connect(parent.randomize_all_fields)
            bio_btn.clicked.connect(parent.generate_story_paragraph)
            self.save_btn.clicked.connect(lambda: parent.force_manual_save_out())

            self.story_background_poll_timer = QTimer()
            self.story_background_poll_timer.timeout.connect(parent.refresh_ui_safely)
            self.story_background_poll_timer.start(500)
            parent.refresh_ui_safely()

    def shutdown(self):
        self.glob.env.logLine(1, "[Make Story shutdown ")
        if self.story_background_poll_timer is not None:
            self.story_background_poll_timer.stop()

        if self.panel:
            self.panel.close()
            self.panel.deleteLater()

        if self.dock:
            self.main_window.removeDockWidget(self.dock)
            self.dock.close()
            self.dock.deleteLater()

        self.dock = None
        self.panel = None


    def initialize(self, docked=False):
        """
        the initialize function for this dock panel
        docked: if false, then standalone version is used
        """
        if self.pluginname in self.repo:
            # if loaded second time
            # Clean up old references just in case
            self.shutdown()

        # create the dock widget including UI
        #
        if docked:
            self.dock = QDockWidget("Character Profile & Story", self.main_window)
            self.dock.setObjectName("MH2_CharacterStory_Dock")
            self.dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
            self.panel = self.Panel(self)
            self.dock.setWidget(self.panel)
            if hasattr(self.main_window, "addDockWidget"):
                self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock)
            else:
                self.dock.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            self.dock.show()
        else:
            self.panel = self.Panel(self)

        # now add plugin to repository
        #
        self.repo[self.pluginname] = self
        return True

def load_extension(app_reference, glob_reference=None):
    """
    MH2 COMPLIANCE HOOK: Spawns the panel container safely
    within the native dashboard interface framework.
    """
    glob_reference.env.logLine(1, "[Make Story] Initializing ...")

    pluginname = os.path.abspath(__file__)
    plugin = MakeStoryPanel(app_reference, glob_reference, pluginname)
    return plugin.initialize(True)


def unload_extension(glob):
    pluginname = os.path.abspath(__file__)
    if pluginname in glob.pluginRepo:
        glob.pluginRepo[pluginname].shutdown()
        glob.pluginRepo.pop(pluginname)     # and delete from repo


