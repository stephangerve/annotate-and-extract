import os
import shutil
from Config import *





if __name__ == "__main__":
    #dir  = "C:\\Users\\Stephan\OneDrive\\Exercise Packs\\Probability, Statistics, and Random Processes\\Miller - Freund's Mathematical Statistics with Applications - 8th\\Solutions Images\\01"
    dir = temp_ss_path
    #section_str = "03.07"
    section_str = None
    MAX = 3
    dne_numbers = [num for num in range(1, MAX + 1)]
    exe_or_sol = "Solution "
    for dne_num in dne_numbers:
        if section_str is not None:
            filename = section_str + " -- " + exe_or_sol + str(dne_num).zfill(3) + ".DNE"
        else:
            files = os.listdir(dir)
            filename = files[0].split(" ")[0] + " -- " + exe_or_sol + str(dne_num).zfill(3) + ".DNE"
        if not os.path.exists(os.path.join(dir, filename.split(".DNE")[0] + ".png")) and not os.path.exists(os.path.join(dir, filename)):
            with open(os.path.join(dir, filename), 'wb') as file:
                file.close()
            print("File created: " + filename)
