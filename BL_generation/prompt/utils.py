# category_mappings.py
# Utility file containing mappings of categories to 'home' or 'public',
# separated by part of speech (nouns, verbs, adjectives).

# ---------------------
# WordBank Noun Mappings
# ---------------------
WORD_BANK_NOUNS = {
    "animals": "public",
    "body_parts": "home",
    "clothing": "home",
    "food_drink": "home",
    "furniture_rooms": "home",
    "games_routines": "public",
    "household": "home",
    "outside": "public",
    "people": "public",
    "places": "public",
    "toys": "home",
    "vehicles": "public",
    "time_words": "public",
}

# ---------------------
# AoA Noun Mappings
# ---------------------
AOA_NOUNS = {
    # ---------------- Home (≈3456) ----------------
    "attribute": "home",
    "artifact_other": "home",
    "cognition": "home",
    "body_part": "home",
    "clothing": "home",
    "food_other": "home",
    "container": "home",
    "room": "home",
    "furniture": "home",
    "beverage": "home",
    "fruit": "home",
    "vegetable": "home",
    "meat": "home",
    "fish": "home",
    "utensil": "home",
    "appliance": "home",
    "grain": "home",
    "dairy": "home",
    "dessert": "home",
    "flower": "home",
    "fabric": "home",
    "writing_implement": "home",
    "emotion": "home",
    "relation": "home",
    "material": "home",
    "substance_other": "home",
    "metal": "home",
    "gas": "home",
    "liquid": "home",
    "chemical_element": "home",
    "Tops": "home",
    "toy": "home",
    "footwear": "home",
    "hand_tool": "home",
    "process": "home",
    "unknown": "home",

    # ---------------- Public (≈3452) ----------------
    "person": "public",
    "event_other": "public",
    "communication_other": "public",
    "device": "public",
    "location_other": "public",
    "structure": "public",
    "quantity": "public",
    "vehicle": "public",
    "time_period": "public",
    "mammal": "public",
    "animal_other": "public",
    "communication_written": "public",
    "building": "public",
    "plant_other": "public",
    "bird": "public",
    "group": "public",
    "social_event": "public",
    "weapon": "public",
    "object": "public",
    "phenomenon": "public",
    "insect": "public",
    "communication_spoken": "public",
    "musical_instrument": "public",
    "sport": "public",
    "tree": "public",
    "body_of_water": "public",
    "reptile": "public",
    "tool": "public",
    "game": "public",
    "travel": "public",
    "natural_elevation": "public",
    "electronic_equipment": "public",
    "time_unit": "public",
    "city": "public",
    "country": "public",
    "landform": "public",
    "arachnid": "public",
    "state": "public",
    "amphibian": "public",
}

AOA_VERBS = {
    "motion": "public",          # run, jump, walk → still public
    "contact": "public",         # hit, push, throw
    "consumption": "home",       # eat, drink
    "communication": "home",     # talk, say, ask
    "social": "public",          # play, hug, share
    "perception": "home",        # see, hear, smell
    "body_action": "home",       # sleep, cry, smile
    "cognition_action": "home",  # think, know, remember
    "creation": "home",          # moved from public → draw, make, build (home crafts)
    "change": "home",            # open, close, break → often home-based
    "competition": "public",     # race, win, lose
    "weather": "public",         # rain, snow
    "possession": "home",        # have, hold
    "stative": "home",           # be, is, seem
    "verb_other": "public",      # happen, exist
}
WORD_BANK_VERBS = {
    "action_words": "public",       # general/active verbs
    "contact": "public",
    "motion": "public",
    "change": "home",               # switched → home (open, close, break)
    "creation": "home",             # switched → home (make, draw, build)
    "possession": "home",
    "stative": "home",
    "cognition_action": "home",
    "body_action": "home",
    "social": "public",              
    "consumption": "home",
    "communication": "home",
    "communication_other": "public",
    "perception": "home",
    "verb_other": "public",
    "travel": "public",
    "competition": "public",
}