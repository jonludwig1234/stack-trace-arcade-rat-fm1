import re
import os
from generate_upgraded_engines import get_upgraded_engines_code

print("=== APPLYING SUPERCHARGED DEMOS, GRAPHICS & USER-FRIENDLY UX ===")

# 1. Update tools/build_all_playable_games.py with the upgraded engines
with open("tools/build_all_playable_games.py", "r") as f:
    bag = f.read()

# Replace generate_playable_arcade_engines() content in build_all_playable_games.py
new_engines = get_upgraded_engines_code()

s_def = bag.find("def generate_playable_arcade_engines():")
e_def = bag.find("def update_builder():")
assert s_def != -1 and e_def != -1, "Cannot find generate_playable_arcade_engines in build_all_playable_games.py"

new_bag = bag[:s_def] + "def generate_playable_arcade_engines():\n    return \"\"\"" + new_engines + "\"\"\"\n\n" + bag[e_def:]
with open("tools/build_all_playable_games.py", "w") as f:
    f.write(new_bag)
print("Successfully updated tools/build_all_playable_games.py with upgraded engines!")

# 2. Now run build_all_playable_games.py to splice the new engines into tools/build_hardware_template.py
import build_all_playable_games
build_all_playable_games.update_builder()
print("Successfully spliced upgraded engines into tools/build_hardware_template.py!")

