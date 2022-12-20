import os
from Config import *




def queryString(add_row, audit_df):
    audit_df_columns = audit_df.columns
    query_string = ''
    for i in range(len(add_row)):
        query_string = query_string + audit_df_columns[i] + " == \"" + str(add_row[i])
        if i == len(add_row) - 1:
            query_string += "\""
        else:
            query_string += "\" and "
    return query_string



def entryExists(add_row, audit_df):
    query_string = queryString(add_row, audit_df)
    if audit_df.query(query_string).empty == True:
        return False
    elif audit_df.query(query_string).empty == False:
        return True



def returnEntries(add_row, audit_df):
    query_string = queryString(add_row, audit_df)
    return audit_df.query(query_string)



#def addSetsList(category, textbook_author, textbook_title, textbook_edition, inc_wksht_df):
def addSetsList(category, textbook_author, textbook_title, textbook_edition, cursor):
    sets_paths = []
    if not os.path.exists(os.path.join(e_packs_dir, category)):
        os.mkdir(os.path.join(e_packs_dir, category))
    if edition != "1st":
        e_packs_txtbk_dir = os.path.join(e_packs_dir, category, " - ".join([author, textbook, edition]))
    else:
        e_packs_txtbk_dir = os.path.join(e_packs_dir, category, " - ".join([author, textbook]))
    if not os.path.exists(e_packs_txtbk_dir):
        os.mkdir(e_packs_txtbk_dir)
    if not os.path.exists(os.path.join(e_packs_txtbk_dir, "Exercises Images")):
        os.mkdir(os.path.join(e_packs_txtbk_dir, "Exercises Images"))
    if not os.path.exists(os.path.join(e_packs_txtbk_dir, "Exercises Images", "Masked")):
        os.mkdir(os.path.join(e_packs_txtbk_dir, "Exercises Images", "Masked"))
    if not os.path.exists(os.path.join(e_packs_txtbk_dir, "Exercises Images", "Unmasked")):
        os.mkdir(os.path.join(e_packs_txtbk_dir, "Exercises Images", "Unmasked"))
    if not os.path.exists(os.path.join(e_packs_txtbk_dir, "Solutions Images")):
        os.mkdir(os.path.join(e_packs_txtbk_dir, "Solutions Images"))

    row_query = "Category = '" + category + "' AND Authors = '" + textbook_author + "' AND Title = '" + textbook_title + "' AND Edition = '" + textbook_edition + "'"
    query = ("SELECT TextbookID FROM textbooks WHERE " + row_query)
    cursor.execute(query)
    id = cursor.fetchall()[0][0]
    query = ("SELECT ChapterNumber, SectionNumber FROM sections WHERE TextbookID = '" + id + "' and AllExercisesExtracted = '0'")
    cursor.execute(query)
    entries = cursor.fetchall()
    sets_list = [list(entry) for entry in entries]
    for set in sets_list:
        if set[0].isdigit():
            if int(set[0]) < 10:
                chapter = "0" + str(set[0])
            else:
                chapter = str(set[0])
        else:
            chapter = str(set[0])
        if set[1].isdigit():
            if int(set[1]) != 0:
                if int(set[1]) < 10:
                    section = "0" + str(set[1])
                else:
                    section = str(set[1])
            else:
                section = "00"
        else:
            section = str(set[1])
        if IMAGE_TYPE == "Exercises":
            set_dir_masked = os.path.join(e_packs_txtbk_dir, "Exercises Images", "Masked", chapter)
            if not os.path.exists(set_dir_masked):
                os.mkdir(set_dir_masked)
            set_dir_unmasked = os.path.join(e_packs_txtbk_dir, "Exercises Images", "Unmasked", chapter)
            if not os.path.exists(set_dir_unmasked):
                os.mkdir(set_dir_unmasked)
            sets_paths.append([[chapter, section], {"masked": set_dir_masked, "unmasked": set_dir_unmasked}])
        elif IMAGE_TYPE == "Solutions":
            set_dir = os.path.join(e_packs_txtbk_dir, "Solutions Images", chapter)
            if not os.path.exists(set_dir):
                os.mkdir(set_dir)
            sets_paths.append([[chapter, section], set_dir])
        print("Set added: " + str(sets_paths[-1][0]))
    if len(sets_paths) == 0:
        print("Finished.")
        print("------------------------------------------")
        exit()
    else:
        print(str(len(sets_paths)) + " sets added.")
        print("------------------------------------------")
        return sorted(sets_paths), e_packs_txtbk_dir
