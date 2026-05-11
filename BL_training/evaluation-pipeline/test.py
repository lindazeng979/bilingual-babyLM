from promptsource.templates import DatasetTemplates
dt = DatasetTemplates("blimp/causative")
print(dt.templates.keys())  # should now include "null_prompt"