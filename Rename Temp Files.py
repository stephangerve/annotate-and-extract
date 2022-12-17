import os
import shutil
from Config import *





if __name__ == "__main__":
    #dir  = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs\\Mathematical Statistics and Statistical Theory\\Deshmukh - Asymptotic Statistical Inference\\Solutions Images\\06"
    dir = temp_ss_path
    section_str = "02.01"
    #section_str = None
    #exe_or_sol = "Solution "
    exe_or_sol = "Exercise "
    for file in os.listdir(dir):
        if section_str is not None:
            new_filename = section_str + " -- " + exe_or_sol + file.split(" ")[-1]
        else:
            new_filename = file.split(" ")[0] + " -- " + exe_or_sol + file.split(" ")[-1]
        shutil.move(os.path.join(dir, file), os.path.join(dir, new_filename))
        print(file + " renamed to " + new_filename)


    # dir = temp_ss_path
    # exe_or_sol = "Solution "
    # files = os.listdir(dir)
    # for file in files:
    #     if ").png" in file:
    #         os.remove(os.path.join(dir, file))
    #     elif "Chapter" in file:
    #         try:
    #             ch_str = int(file.split("Chapter")[-1].split(",")[0].split(".")[0])
    #         except:
    #             ch_str = file.split("Chapter")[-1].split(",")[0].split(".")[0]
    #         try:
    #             sect_str = int(file.split("Chapter")[-1].split(",")[0].split(".")[1])
    #         except:
    #             sect_str = 0
    #         try:
    #             section_str = ".".join([str(ch_str).zfill(2), str(sect_str).zfill(2)])
    #         except:
    #             section_str = ".".join([str(ch_str), str(sect_str).zfill(2)])
    #         exnum = int(file.split(" ")[-1].split("E.png")[0])
    #         new_filename = section_str + " -- " + exe_or_sol + str(exnum).zfill(3) + ".png"
    #         shutil.move(os.path.join(dir, file), os.path.join(dir, new_filename))
    #         print(file + " renamed to " + new_filename)


    # dir_exercises = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs\\Probability, Statistics, and Random Processes\\Devore - Modern Mathematical Statistics with Applications - 3rd\\Exercises Images"
    # dir_solutions = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs\\Probability, Statistics, and Random Processes\\Devore - Modern Mathematical Statistics with Applications - 3rd\\Solutions Images"
    # chapters_exe = os.listdir(dir_exercises)
    # chapters_sol = os.listdir(dir_solutions)
    # for chapter in chapters_exe:
    #     files_exe = os.listdir(os.path.join(dir_exercises, chapter))
    #     for i in range(len(files_exe), 0, -1):
    #         file = files_exe[i - 1]
    #         new_filename = " ".join(file.split(" ")[:-1]) + " " + str(i).zfill(3) + ".png"
    #         shutil.move(os.path.join(dir_exercises, chapter, file), os.path.join(dir_exercises, chapter, new_filename))
    #         print(file + " renamed to " + new_filename)

    # dir = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
    # NUM_DIRS = 1
    # for i in range(NUM_DIRS):
    #     # dir_exercises = os.path.join(dir, "Exercises Images", str(i + 1).zfill(2))
    #     dir_exercises = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
    #     files_exe = os.listdir(os.path.join(dir_exercises))
    #     files_exe.sort()
    #     MAX = len(files_exe)
    #     index = 0
    #     for file in files_exe:
    #         new_filename = " ".join(file.split(" ")[:-1]) + " " + str(index).zfill(3) + ".png"
    #         shutil.move(os.path.join(dir_exercises, file), os.path.join(dir_exercises, new_filename))
    #         print(file + " renamed to " + new_filename)
    #         index += 1


    # dir = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
    # NUM_DIRS = 1
    # for i in range(NUM_DIRS):
    #     #dir_exercises = os.path.join(dir, "Exercises Images", str(i + 1).zfill(2))
    #     dir_exercises = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
    #     files_exe = os.listdir(os.path.join(dir_exercises))
    #     files_exe.sort()
    #     index = len(files_exe)
    #     for file in reversed(files_exe):
    #         new_filename = " ".join(file.split(" ")[:-1]) + " " + str(index).zfill(3) + ".png"
    #         shutil.move(os.path.join(dir_exercises, file), os.path.join(dir_exercises, new_filename))
    #         print(file + " renamed to " + new_filename)
    #         index -= 1
        # dir_solutions = os.path.join(dir, "Solutions Images", str(i + 1).zfill(2))
        # files_exe = os.listdir(os.path.join(dir_solutions))
        # files_exe.sort()
        # index = len(files_exe)
        # for file in reversed(files_exe):
        #     new_filename = " ".join(file.split(" ")[:-1]) + " " + str(index).zfill(3) + ".png"
        #     shutil.move(os.path.join(dir_solutions, file), os.path.join(dir_solutions, new_filename))
        #     print(file + " renamed to " + new_filename)
        #     index -= 1

    # dir_exercises = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs\\Probability, Statistics, and Random Processes\\Miller - Freund's Mathematical Statistics with Applications - 8th\\Solutions Images\\03"
    # MAX = 136
    # STOP = 6
    # files_exe = os.listdir(os.path.join(dir_exercises))
    # files_exe.sort()
    # j = len(files_exe) - 1
    # for i in range(MAX, STOP, -1):
    #     file = files_exe[j]
    #     new_filename = " ".join(file.split(" ")[:-1]) + " " + str(i).zfill(3) + ".png"
    #     shutil.move(os.path.join(dir_exercises, file), os.path.join(dir_exercises, new_filename))
    #     print(file + " renamed to " + new_filename)
    #     j -= 1


    # dir_exercises = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs\\Probability, Statistics, and Random Processes\\Miller - Freund's Mathematical Statistics with Applications - 8th\\Solutions Images\\02"
    # START = 1
    # END = 34
    # START_INDEX = 6
    # files_exe = os.listdir(os.path.join(dir_exercises))
    # files_exe.sort()
    # for i in range(START, END + 1):
    #     file = files_exe[i]
    #     new_filename = " ".join(file.split(" ")[:-1]) + " " + str(START_INDEX).zfill(3) + ".png"
    #     shutil.move(os.path.join(dir_exercises, file), os.path.join(dir_exercises, new_filename))
    #     print(file + " renamed to " + new_filename)
    #     START_INDEX += 1