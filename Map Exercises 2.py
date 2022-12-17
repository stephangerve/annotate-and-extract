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
              "Variational Calculus",
              "Grinstead - Introduction to Probability",
              "Devore - Probability and Statistics - 7th",
              "",
              "",
              "",
              "",
              ]
    missing_solutions = []
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
                        if len(solutions) > 0:
                            for exercise in exercises:
                                sol_of_exe = exercise.split(" Exercise ")[0] + " Solution " + exercise.split(" Exercise ")[1]
                                sol_of_exe_dne = ".".join(sol_of_exe.split(".")[:-1]) + ".DNE"
                                if sol_of_exe not in solutions and sol_of_exe_dne not in solutions:
                                    row = [category, textbook, chapter, sol_of_exe]
                                    missing_solutions.append(row)
                                    print(row)

    missing_solutions_df = pd.DataFrame(missing_solutions, columns=[  'Category',
                                                                    'Textbook',
                                                                    'Chapter',
                                                                    'Missing',
                                                                    ])
    missing_solutions_df.to_csv(os.path.join("C:\\Users\\Stephan\\OneDrive\\Worksheet Project", "Missing Solutions.csv"), index=False, header=True)
    os.startfile(os.path.join("C:\\Users\\Stephan\\OneDrive\\Worksheet Project", "Missing Solutions.csv"))

