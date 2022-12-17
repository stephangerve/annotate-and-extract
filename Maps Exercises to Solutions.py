import keyboard
import time
import pandas as pd
import os
e_packs_dir = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs"


if __name__ == "__main__":
    ignore = ["Regression Analysis and Generalized Linear Models",
              "Signals and Systems",
              "Statistical and Adaptive Signal Processing",
              "Time Series Analysis",
              "Ordinary Differential Equations",
              "Optimization",
              "Multivariate Statistics",
              "Mathematical Economics",
              "Linear Algebra",
              "Discrete Mathematics",
              "Digital Signal Processing",
              "Bayesian Statistics",
              "AI, Machine Learning, and Data Science",
              "",
              "",
              "",
              "",
              "",
              ]
    complete_packs = []
    incomplete_packs = []
    categories = os.listdir(e_packs_dir)
    for category in categories:
        if category not in ignore:
            cat_dir = os.path.join(e_packs_dir, category)
            textbooks = os.listdir(cat_dir)
            for textbook in textbooks:
                if textbook not in ignore:
                    txtbk_dir = os.path.join(cat_dir, textbook)
                    exercises_images_dir = os.path.join(txtbk_dir, "Exercises Images")
                    solutons_images_dir = os.path.join(txtbk_dir, "Solutions Images")
                    chapters = os.listdir(exercises_images_dir)
                    for chapter in chapters:
                        if os.path.exists(os.path.join(exercises_images_dir, chapter)):
                            exercises = os.listdir(os.path.join(exercises_images_dir, chapter))
                        else:
                            exercises = []
                        if os.path.exists(os.path.join(solutons_images_dir, chapter)):
                            solutions = os.listdir(os.path.join(solutons_images_dir, chapter))
                        else:
                            solutions = []
                        row = [category, textbook, chapter, len(exercises), len(solutions)]
                        if (len(exercises) != len(solutions)) and (len(exercises) > 0):
                            incomplete_packs.append(row)
                        elif (len(exercises) == len(solutions)) and (len(exercises) > 0 and len(solutions) > 0):
                            complete_packs.append(row)
                            print(str(row))
    incomplete_packs_df = pd.DataFrame(incomplete_packs, columns=[  'Category',
                                                                    'Textbook',
                                                                    'Chapter',
                                                                    'Exercises',
                                                                    'Solutions',
                                                                    ])
    incomplete_packs_df.to_csv(os.path.join("C:\\Users\\Stephan\\OneDrive\\Worksheet Project", "Incomplete packs.csv"), index=False, header=True)
    os.startfile(os.path.join("C:\\Users\\Stephan\\OneDrive\\Worksheet Project", "Incomplete packs.csv"))

    complete_packs_df = pd.DataFrame(complete_packs, columns=['Category',
                                                                  'Textbook',
                                                                  'Chapter',
                                                                  'Exercises',
                                                                  'Solutions',
                                                                  ])
    complete_packs_df.to_csv(os.path.join("C:\\Users\\Stephan\\OneDrive\\Worksheet Project", "Complete packs.csv"),
                               index=False, header=True)
    os.startfile(os.path.join("C:\\Users\\Stephan\\OneDrive\\Worksheet Project", "Complete packs.csv"))

