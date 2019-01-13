# Enter machine commands here
# Use any Python that creates GCode strings
# and calls emit() on them: e.g. emit("G91")
#
# You may browse available GCode modules
# at the bottom of this page

from gcode_modules.snowman import code as snowman

emit(translate_and_scale(snowman(), scale=0.1))
