# Enter machine commands here
# Use any Python that prints G-code
# You may browse available modules at the bottom of this page

from gcode_modules.snowman import code as snowman

print(translate_and_scale(snowman(), scale=0.1))
