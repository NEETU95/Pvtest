import re
#import stanza
import spacy
import pandas as pd
from PyPDF2 import PdfReader


# # EXtract patient details gender
# reader = PdfReader('Sosa NH..pdf')
#
# # Get the number of pages in the PDF
# num_pages = len(reader.pages)
#
# # Initialize an empty string to store the extracted text
# all_text = ""
#
# # Loop through all pages and extract text
# for page_num in range(num_pages):
#     page = reader.pages[page_num]
#     text = page.extract_text()
#     all_text += text  # Append the text from the current page to the overall text

# print(all_text)

def get_parent_text(source_text, en_core, bcd5r):
    all_text = source_text

    nlp_1=en_core
    nlp= bcd5r
    title = ""
    print("Protect Confidentiality: Yes")
    print("Title:", title)

    report_to_discussion = ""
    first_three_lines = ""
    case_keywords = ["Case Presentation", "Case Summary", "Case History", "Case description", "Case Report"]
    found_case_type = None
    text_after_case_type = ""

    doc = nlp(all_text)
    for keyword in case_keywords:
        if keyword in all_text:
            found_case_type = keyword
            break
    if "An official website of the United States government" in all_text:
        word_index = doc.text.find("Affiliations")
        word_index_keyword = doc.text.find("Keywords")
        print(word_index_keyword)
        extracted_text = doc.text[word_index:word_index_keyword]
        # text_lines = text_after_case_type.split('\n')
        first_three_lines = extracted_text
        report_to_discussion = extracted_text
    elif found_case_type == "Case Report":
        search_term = "Case Report"
        count = 0
        found_start_line = -1
        second_report_to_discussion = ""
        end_line = -1
        final_text = ""
        for i, line in enumerate(all_text.split('\n')):
            if search_term in line:
                count += 1
                found_start_line = i
            if "Discussion" in line:
                end_line = i
        print("count is", count)
        if count > 0 and found_start_line != -1:
            # Extract the found line and the subsequent 7 lines
            extracted_lines = all_text.split('\n')[(found_start_line + 1):end_line]

            print(found_start_line)
            print(extracted_lines)
            report_to_discussion = '\n'.join(extracted_lines)
            print("report from 1", report_to_discussion)
            for i, line in enumerate(report_to_discussion.split('\n')):
                if "Case" and "Report" in line:
                    count += 1
                    found_start_line = i
            if count > 1:
                extracted_lines = report_to_discussion.split('\n')[found_start_line:end_line]

                print("##########f", found_start_line)
                print("##########", extracted_lines)
                second_report_to_discussion = '\n'.join(extracted_lines)
            if second_report_to_discussion:
                final_text = second_report_to_discussion
            else:
                final_text = report_to_discussion

            print("second count", count)
            first_three_lines_split = final_text.split("\n")[:10]
            first_three_lines = '\n'.join(first_three_lines_split)
        # if count > 0:
        #     extracted_text = doc.text[word_index:]
        #     text_lines = extracted_text.split('\n')
        #     first_three_lines = '\n'.join(text_lines[:8])
    else:
        # print("Found case type:", found_case_type)
        word_index = doc.text.find(found_case_type)
        end_word_index = doc.text.find("Discussion")
        # Extract text after the specific word
        extracted_text = doc.text[word_index + len(found_case_type):  end_word_index]
        text_after_case_type = all_text.split(found_case_type, 1)[-1]
        text_lines = extracted_text.split('\n')
        report_to_discussion = '\n'.join(text_lines)
        first_three_lines_split = report_to_discussion.split("\n")[:10]
        first_three_lines = '\n'.join(first_three_lines_split)

    # Extract the first three lines
    # print("from another document:", report_to_discussion)

    # print("first three#########", first_three_lines)

    mother_comments = ""
    father_comments = ''
    patient_gender = ["Male", "Female"]
    ethnic_groups = [
        "African American",
        "American Indian or Alaska Native",
        "Asian",
        "Black",
        "Caucasian",
        "Native Hawaiian or Other Pacific",
        "Other",
        "White"
    ]
    groups = [
        "African American",
        "American Indian",
        "Alaska Native",
        "Asian",
        "Black",
        "Caucasian",
        "Native Hawaiian",
        "Other Pacific",
        "Other",
        "White"]
    print(first_three_lines)
    lines = first_three_lines.split()
    mother_father_keywords = ["mother", "father"]
    mother_first_name = ""
    mother_middle_name = ""
    mother_last_name = ""
    initials = ""
    mother_llt = []
    mother_age = ""
    sex = ""
    time_unit = ""
    dob = ""
    group = ""
    ethnic = ""
    weight = ""
    units = " "
    height = ""
    inches = ""
    height_in_cm = ""
    parent_breast_feeding = ["Yes", "No"]
    lmp = ""
    gestation_period = ""
    gestation_period_units = ""
    start_date = ""
    end_date = ""
    continuing = ""
    llt = []
    comments = ""
    llt_indicators_string = ""
    llt_reactions_string = ""
    llt_indicators = []
    indication_text = ""
    drug_name = ""
    llt_reactions = []
    reaction_comment = ""
    start_line = None
    mother_father_keyword = ""
    cleaned_comments = ""
    end_line = -1
    for num, row in enumerate(lines):
        for keyword in mother_father_keywords:
            if keyword in row:
                mother_father_keyword = keyword
                print(row)

                # Find the start and end indices of the relevant portion of the line
                start_line = row.find(keyword)

                # Accumulate the text from the current line
                mother_text = row[start_line:]

                # Check if there is a full stop in the remaining text
                while end_line == -1 and num + 1 < len(lines):
                    num += 1
                    next_line = lines[num]
                    mother_text += ' ' + next_line
                    end_line = mother_text.find('.')

                # Extract the text up to the full stop
                mother_comments += mother_text[:end_line + 1] + "\n"
                print("mother comm", mother_comments)
                # Extracting starts
    cleaned_comments = mother_comments.replace(' - ', '-')
    print("cleaned_comm", cleaned_comments)
    if start_line is not None and mother_father_keyword == mother_father_keywords[0]:

        doc = nlp_1(cleaned_comments)
        current_name = ""
        parent_name = ""
        for token in doc:
            if token.ent_type_ == "PERSON":
                current_name += token.text + " "
            else:
                if current_name.strip():
                    parent_name += current_name.strip() + " "
                    current_name = ""

        # Handle the last name if present
        if current_name.strip():
            parent_name += current_name.strip()

        # Remove duplicate names
        patient_name = ' '.join(list(dict.fromkeys(parent_name.split())))
        print(patient_name)
        name_parts = patient_name.split()
        num_words = len(name_parts)
        if num_words == 2:
            # If the author name has only 2 words, consider them as first and last names
            mother_first_name = name_parts[0]
            mother_last_name = name_parts[1]
        elif num_words == 0:
            mother_first_name = "Unk"
        elif num_words == 1:
            mother_first_name = name_parts[0]
        elif num_words >= 3:
            mother_first_name = name_parts[0]
            mother_middle_name = name_parts[1]
            mother_last_name = " ".join(name_parts[2:])

        print("Mother First name:", mother_first_name)

        print("Mother middle name:", mother_middle_name)

        print("Mother last name:", mother_last_name)

        # Initials

        if mother_first_name == 'Unk':
            initials = 'Unk'
        elif not mother_last_name:
            initials = mother_first_name[0]
        else:
            initials = mother_first_name[0] + mother_last_name[0]
        print("Initials:", initials)

        # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None,use_gpu=False)

        # Age

        time_units = ["Year", "Decade"]
        # Regular expression pattern to match age information with hyphen and different time units
        pattern = r'(\d+)\s*-?\s*(' + '|'.join(time_units) + ')'
        age_pattern = re.compile(pattern)
        matches = age_pattern.findall(cleaned_comments)
        if matches:
            ages, time_unit_ = int(matches[0][0]), matches[0][1]
            match_index = first_three_lines.find(matches[0][1], first_three_lines.find(matches[0][0]))
            if match_index != -1 and first_three_lines.find("old", match_index) != -1:
                mother_age = ages
                time_unit = time_unit_
        print("Mother Age at time of onset of reaction:", mother_age)

        # Extract units
        print("Mother Age at time of onset of reaction(units):", time_unit)

        # Date of birth

        dob_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
        matches = dob_pattern.findall(cleaned_comments)
        if matches:
            dob = matches[0]
        print("Date of birth:", dob)

        sex = patient_gender[1]
        print("Sex:", sex)

        # GROUP TYPE

        for group_type in groups:
            if group_type in cleaned_comments.split(" "):
                group = group_type
        if group == "African American":
            ethnic = ethnic_groups[0]
        elif group == "American Indian" or group == "Alaska Native":
            ethnic = ethnic_groups[1]
        elif group == "Asian":
            ethnic = ethnic_groups[2]
        elif group == "Black":
            ethnic = ethnic_groups[3]
        elif group == "Caucasian":
            ethnic = ethnic_groups[4]
        elif group == "Native Hawaiian" or group == "Other Pacific":
            ethnic = ethnic_groups[5]
        elif group == "White":
            ethnic = ethnic_groups[7]
        print("Mother Ethnic_group:", ethnic)

        # Weight

        # Regular expression pattern to match weights with various units
        weight_pattern = re.compile(r'(\d+(\.\d+)?)\s*(kgs?|grams?|g|Kilo\s*grams?)', re.IGNORECASE)

        # Find all matches in the text
        matches = weight_pattern.findall(cleaned_comments)
        sentence = ""
        # Extract weights and units if matches are found

        if any(word in cleaned_comments.lower() for word in ['weigh']):
            if units in ["g", "grams"]:
                converted_weight = int(weight) / 1000
                weight = converted_weight
            elif units.lower() in ["lbs", "pounds"]:
                # Convert pounds to kilograms (1 lb = 0.453592 kg)
                converted_weight = int(weight) * 0.453592
                weight = converted_weight
            else:
                weight = weight
        print(" Mother Weight (kg):", weight)

        # Height

        # Regular expression pattern to match heights in various units
        height_pattern = re.compile(r'(\d+)\s*(cm|centimeters|feet|ft)\s*(\d+)?\s*(inches)?', re.IGNORECASE)

        # Find all matches in the text
        matches = height_pattern.finditer(cleaned_comments)

        # Extract heights and units if matches are found
        for match in matches:
            height, units, inches, _ = match.groups()
            # Find the entire sentence containing the height information
            sentence_start = max(0, cleaned_comments.rfind('.', 0, match.start()))

        if any(word in cleaned_comments.lower() for word in ['height', 'tall']):
            if units.lower() in ['feet', 'ft']:
                height_in_cm = int(height) * 30.48  # Convert feet to cm
                if inches:
                    height_in_cm += int(inches) * 2.54  # Convert inches to cm
                print(" Mother Height (cm):", height_in_cm)
            else:
                height_in_cm = height
                print("Mother Height (cm):", height_in_cm)
        else:
            print("Mother Height (cm):", height_in_cm)

        feeding_keywords = ["feeding", "milk"]
        feeding_comments = ""
        lines = first_three_lines.split()
        for i, line in enumerate(lines):
            for feeding_keyword in feeding_keywords:
                if feeding_keyword in line:
                    # Find the start and end indices of the relevant portion of the line
                    start_line = line.find(feeding_keyword)

                    # Accumulate the text from the current line
                    mother_text = line[start_line:]
                    # Check if there is a full stop in the remaining text
                    end_line = mother_text.find('.')
                    while end_line == -1 and i + 1 < len(lines):
                        i += 1
                        next_line = lines[i]
                        mother_text += ' ' + next_line
                        end_line = mother_text.find('.')

                    # Extract the text up to the full stop
                    feeding_comments += mother_text[:end_line + 1] + "\n"

        menstrual_period = ['lmp', 'l.m.p', 'last menstrual period']
        estimation_delivery_date = ['edd', 'estimation delivery date']
        if sex == patient_gender[1]:

            for word in menstrual_period:
                if word in first_three_lines.lower():
                    sentence_start = max(0, first_three_lines.rfind('.', 0, first_three_lines.lower().find(word)))
                    sentence_end = first_three_lines.find('.', first_three_lines.lower().find(word))
                    sentence = first_three_lines[sentence_start:sentence_end].strip()

                    # Search for a date pattern in the same sentence
                    date_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
                    date_match = date_pattern.search(sentence)
                    if date_match:
                        lmp = date_match.group(1)
            print("Last Menstrual period", lmp)

        # Gestation period

        gestation_period_unit = ["trimester", "day", "month", "week"]
        # Regular expression pattern to match age information with hyphen and different time units
        pattern = r'(\d+)\s*-?\s*(' + '|'.join(gestation_period_unit) + ')'
        gestation_period_pattern = re.compile(pattern)
        matches = gestation_period_pattern.findall(first_three_lines)
        if matches:
            gestation_period, gestation_period_units = int(matches[0][0]), matches[0][1]
        print("Gestation period::", gestation_period)
        print("Gestation period units:", gestation_period_units)

        # mother medical history

        lines = cleaned_comments.split()
        pattern = re.compile(
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        )
        match = re.search(pattern, cleaned_comments)
        if match:
            matched_date = match.group()
            start_date = matched_date
        match_end = re.search(pattern, cleaned_comments)
        if match_end:
            matched_end_date = match_end.group()
            if matched_end_date != start_date:
                end_date = matched_end_date

        print("Start date:", start_date)
        print("End date:", end_date)

        # Continuing

        continuing_list = ['true', 'false', 'null']
        if end_date:
            continuing = continuing_list[1]

        if "continu" in cleaned_comments.lower():
            continuing = continuing_list[0]
        else:
            continuing = continuing_list[2]

        print("Continuing:", continuing)

        # LLT
        # Gathering medical history
        history_start = None
        history_end = None
        history_keywords = ["medical history", "history", "he had", "she had", "diagnosed", "suffered"]
        lines = cleaned_comments

        for history_keyword in history_keywords:
            if "mother" in lines and history_keyword in lines:
                print("found mother line")
                if "had no" not in lines or "no history" not in lines:
                    print("history line", lines)
                    # Find the start and end indices of the relevant portion of the line
                    start_line = lines.find(history_keyword)

                    # Accumulate the text from the current line
                    history_text = lines[start_line:]
                    print(history_text)
                    # Check if there is a full stop in the remaining text
                    end_line = history_text.find('.')
                    while end_line == -1 and i + 1 < len(lines):
                        i += 1
                        next_line = lines[i]
                        history_text += next_line
                        end_line = history_text.find('.')

                    # Extract the text up to the full stop
                    comments += history_text[:end_line + 1] + "\n"

        cleaned_comments = comments.replace(' -', '-')

        # bc5cdr_model_path = "stanza_resources\en\ner\bc5cdr.pt"
        # nlp = stanza.Pipeline('en', processors={'ner': bc5cdr_model_path})

        # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None,use_gpu=False)
        # model_folder_path = "C:\Users\chebramu\PycharmProjects\pythonProject1\en_ner_bc5cdr_md-0.5.3"

        doc = nlp(comments)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                mother_llt.append(ent.text)
        if "COVID" in cleaned_comments and "19" in cleaned_comments:
            print("YES")
            mother_llt.append("COVID-19")
        mother_llt_string = ','.join(mother_llt)
        print("LLT", mother_llt_string)
        print("Comments", cleaned_comments)

        # DRUG HISTORY
        text_line = ""
        previous_lines = []
        text_before_medicine = ""
        text_after_medicine = ""
        products = pd.read_excel("product_names.xlsx")
        for line_number, line in enumerate(first_three_lines.split('\n')):
            for drug in products['product_name']:
                if drug.lower() in line.lower() and "mother" in line:
                    line_index = line.lower().find(drug.lower())
                    text_line = line[:line_index + len(drug)]

                    # Combine the current line and the previous lines before the medicine
                    text_before_medicine += "\n".join(previous_lines) + "\n" + text_line + "\n"

                    # Store the lines after the medicine is found
                    text_after_medicine = "\n".join(report_to_discussion.split('\n')[line_number + 1:])

                    # Clear previous_lines for the next iteration
                    previous_lines = []

                    # Stop searching for other drugs in the same line once one is found
                    break

            # Store the current line in previous_lines
            previous_lines.append(line)

        print("Text Before Medicine:")
        print(text_before_medicine)

        print("\nText After Medicine:")
        print(text_after_medicine)

        # Name of drug
        # nlp = spacy.blank("en")
        doc = nlp(text_before_medicine)
        drug_name = []
        for ent in doc.ents:
            if ent.label_ == "CHEMICAL":
                drug_name.append(ent.text)
        drug_name_string = ','.join(drug_name)
        print("LLT", drug_name_string)

        # Indication
        indication_keywords = ["noticed", "observed", "experienced", "suffered", "reported", "developed", "showed",
                               "encountered"]

        text_for_indication = ""
        lines = text_before_medicine.split("\n")
        for i, line in enumerate(lines):
            for indication_keyword in indication_keywords:
                if indication_keyword in line:
                    start_line = line.find(indication_keyword)
                    text_for_indication = line[start_line:]

                    # end_line = death_text.find('.')
                    # death_comments = death_text[:end_line]
        indication_text += text_for_indication + "\n"

        doc = nlp(indication_text)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                llt_indicators.append(ent.text)
        llt_indicators_string = ','.join(llt_indicators)
        print("Indication LLT:", llt_indicators)
        print("Indication Comment:", indication_text)

        # Reaction after drug

        doc = nlp(text_after_medicine)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                llt_reactions.append(ent.text)
        llt_reactions_string = ','.join(llt_reactions)
        print("Reaction LLT:", llt_reactions)
        print("Reaction Comment:", text_after_medicine.split("/n")[:2])
    elif start_line is not None and mother_father_keyword == mother_father_keywords[1]:
        # Extracting starts
        nlp_1 = spacy.load("en_core_web_sm")
        doc = nlp_1(cleaned_comments)
        current_name = ""
        parent_name = ""
        for token in doc:
            if token.ent_type_ == "PERSON":
                current_name += token.text + " "
            else:
                if current_name.strip():
                    parent_name += current_name.strip() + " "
                    current_name = ""

        # Handle the last name if present
        if current_name.strip():
            parent_name += current_name.strip()

        # Remove duplicate names
        patient_name = ' '.join(list(dict.fromkeys(parent_name.split())))
        print(patient_name)
        name_parts = patient_name.split()
        num_words = len(name_parts)
        if num_words == 2:
            # If the author name has only 2 words, consider them as first and last names
            mother_first_name = name_parts[0]
            mother_last_name = name_parts[1]
        elif num_words == 0:
            mother_first_name = "Unk"
        elif num_words == 1:
            mother_first_name = name_parts[0]
        elif num_words >= 3:
            mother_first_name = name_parts[0]
            mother_middle_name = name_parts[1]
            mother_last_name = " ".join(name_parts[2:])

        print("Father First name:", mother_first_name)

        print("Father middle name:", mother_middle_name)

        print("Father last name:", mother_last_name)

        # Initials
        initials = ""
        if mother_first_name == 'UNK':
            initials = 'UNK'
        elif not mother_last_name:
            initials = mother_first_name[0]
        else:
            initials = mother_first_name[0] + mother_last_name[0]
        print("Initials:", initials)

        # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None,use_gpu=False)

        doc = nlp(cleaned_comments)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                mother_llt.append(ent.text)
        if "COVID" in cleaned_comments and "19" in cleaned_comments:
            print("YES")
            mother_llt.append("COVID-19")
        mother_llt_string = ','.join(mother_llt)
        print("LLT", mother_llt)
        print("Comments", cleaned_comments)

        # Age

        mother_age = ""
        time_unit = ""
        time_units = ["Year", "Decade"]
        # Regular expression pattern to match age information with hyphen and different time units
        pattern = r'(\d+)\s*-?\s*(' + '|'.join(time_units) + ')'
        age_pattern = re.compile(pattern)
        matches = age_pattern.findall(cleaned_comments)
        if matches:
            ages, time_unit_ = int(matches[0][0]), matches[0][1]
            match_index = first_three_lines.find(matches[0][1], first_three_lines.find(matches[0][0]))
            if match_index != -1 and first_three_lines.find("old", match_index) != -1:
                mother_age = ages
                time_unit = time_unit_
        print("Father Age at time of onset of reaction:", mother_age)

        # Extract units
        print("Father Age at time of onset of reaction(units):", time_unit)

        # Date of birth
        dob = ""
        dob_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
        matches = dob_pattern.findall(cleaned_comments)
        if matches:
            dob = matches[0]
        print("Date of birth:", dob)

        sex = patient_gender[0]
        print("Sex:", sex)

        group = ""
        ethnic = ""

        for group_type in groups:
            if group_type in cleaned_comments.split(" "):
                group = group_type
        if group == "African American":
            ethnic = ethnic_groups[0]
        elif group == "American Indian" or group == "Alaska Native":
            ethnic = ethnic_groups[1]
        elif group == "Asian":
            ethnic = ethnic_groups[2]
        elif group == "Black":
            ethnic = ethnic_groups[3]
        elif group == "Caucasian":
            ethnic = ethnic_groups[4]
        elif group == "Native Hawaiian" or group == "Other Pacific":
            ethnic = ethnic_groups[5]
        elif group == "White":
            ethnic = ethnic_groups[7]
        print("Mother Ethnic_group:", ethnic)

        # Weight
        weight = ""
        units = " "

        # Regular expression pattern to match weights with various units
        weight_pattern = re.compile(r'(\d+(\.\d+)?)\s*(kgs?|grams?|g|Kilo\s*grams?)', re.IGNORECASE)

        # Find all matches in the text
        matches = weight_pattern.findall(cleaned_comments)
        sentence = ""
        # Extract weights and units if matches are found

        if any(word in cleaned_comments.lower() for word in ['weigh']):
            if units in ["g", "grams"]:
                converted_weight = int(weight) / 1000
                weight = converted_weight
            elif units.lower() in ["lbs", "pounds"]:
                # Convert pounds to kilograms (1 lb = 0.453592 kg)
                converted_weight = int(weight) * 0.453592
                weight = converted_weight
            else:
                weight = weight
        print(" Father Weight (kg):", weight)

        # Height
        height = ""
        inches = ""
        height_in_cm = ""
        # Regular expression pattern to match heights in various units
        height_pattern = re.compile(r'(\d+)\s*(cm|centimeters|feet|ft)\s*(\d+)?\s*(inches)?', re.IGNORECASE)

        # Find all matches in the text
        matches = height_pattern.finditer(cleaned_comments)

        # Extract heights and units if matches are found
        for match in matches:
            height, units, inches, _ = match.groups()
            # Find the entire sentence containing the height information
            sentence_start = max(0, cleaned_comments.rfind('.', 0, match.start()))

        if any(word in cleaned_comments.lower() for word in ['height', 'tall']):
            if units.lower() in ['feet', 'ft']:
                height_in_cm = int(height) * 30.48  # Convert feet to cm
                if inches:
                    height_in_cm += int(inches) * 2.54  # Convert inches to cm
                print("Father Height (cm):", height_in_cm)
            else:
                height_in_cm = height
                print("Father Height (cm):", height_in_cm)
        else:
            print("Father Height (cm):", height_in_cm)
        #
        # feeding_keywords = ["feeding", "milk"]
        # feeding_comments = ""
        # lines = first_three_lines.split()
        # for i, line in enumerate(lines):
        #     for feeding_keyword in feeding_keywords:
        #         if feeding_keyword in line:
        #             # Find the start and end indices of the relevant portion of the line
        #             start_line = line.find(feeding_keyword)
        #
        #             # Accumulate the text from the current line
        #             father_text = line[start_line:]
        #             # Check if there is a full stop in the remaining text
        #             end_line = father_text.find('.')
        #             while end_line == -1 and i + 1 < len(lines):
        #                 i += 1
        #                 next_line = lines[i]
        #                 father_text += next_line
        #                 end_line = father_text.find('.')
        #
        #             # Extract the text up to the full stop
        #             feeding_comments += father_text[:end_line + 1] + "\n"

        # Father medical history

        start_date = ""
        end_date = ""
        lines = cleaned_comments.split()
        pattern = re.compile(
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        )
        match = re.search(pattern, cleaned_comments)
        if match:
            matched_date = match.group()
            start_date = matched_date
        match_end = re.search(pattern, cleaned_comments)
        if match_end:
            matched_end_date = match_end.group()
            if matched_end_date != start_date:
                end_date = matched_end_date

        print("Start date:", start_date)
        print("End date:", end_date)

        # Continuing
        continuing = ""
        continuing_list = ['true', 'false', 'null']
        if end_date:
            continuing = continuing_list[1]

        if "continu" in cleaned_comments.lower():
            continuing = continuing_list[0]
        else:
            continuing = continuing_list[2]

        print("Continuing:", continuing)

        # LLT
        # Gathering medical history
        history_start = None
        history_end = None
        history_keywords = ["medical history", "history", "he had", "she had", "diagnosed", "suffered"]
        lines = cleaned_comments

        for history_keyword in history_keywords:
            if "father" in lines and history_keyword in lines:
                print("found mother line")
                if "had no" not in lines or "no history" not in lines:
                    print("history line", lines)
                    # Find the start and end indices of the relevant portion of the line
                    start_line = lines.find(history_keyword)

                    # Accumulate the text from the current line
                    history_text = lines[start_line:]
                    print(history_text)
                    # Check if there is a full stop in the remaining text
                    end_line = history_text.find('.')
                    while end_line == -1 and i + 1 < len(lines):
                        i += 1
                        next_line = lines[i]
                        history_text += next_line
                        end_line = history_text.find('.')

                    # Extract the text up to the full stop
                    comments += history_text[:end_line + 1] + "\n"

        cleaned_comments = comments.replace(' -', '-')

        # bc5cdr_model_path = "stanza_resources\en\ner\bc5cdr.pt"
        # nlp = stanza.Pipeline('en', processors={'ner': bc5cdr_model_path})

        # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None,use_gpu=False)
        # model_folder_path = "C:\Users\chebramu\PycharmProjects\pythonProject1\en_ner_bc5cdr_md-0.5.3"
        nlp = spacy.load("en_ner_bc5cdr_md")
        doc = nlp(comments)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                mother_llt.append(ent.text)
        if "COVID" in cleaned_comments and "19" in cleaned_comments:
            print("YES")
            mother_llt.append("COVID-19")
        mother_llt_string = ','.join(mother_llt)
        print("LLT", mother_llt_string)
        splitted_mother_llt = mother_llt_string.split(',')
        mother_llt_output = splitted_mother_llt[0]
        print("Comments", cleaned_comments)

        # DRUG HISTORY
        text_line = ""
        previous_lines = []
        text_before_medicine = ""
        text_after_medicine = ""
        products = pd.read_excel("product_names.xlsx")
        for line_number, line in enumerate(first_three_lines.split('\n')):
            for drug in products['product_name']:
                if drug.lower() in line.lower() and "mother" in line:
                    line_index = line.lower().find(drug.lower())
                    text_line = line[:line_index + len(drug)]

                    # Combine the current line and the previous lines before the medicine
                    text_before_medicine += "\n".join(previous_lines) + "\n" + text_line + "\n"

                    # Store the lines after the medicine is found
                    text_after_medicine = "\n".join(report_to_discussion.split('\n')[line_number + 1:])

                    # Clear previous_lines for the next iteration
                    previous_lines = []

                    # Stop searching for other drugs in the same line once one is found
                    break

            # Store the current line in previous_lines
            previous_lines.append(line)

        print("Text Before Medicine:")
        print(text_before_medicine)

        print("\nText After Medicine:")
        print(text_after_medicine)

        # Name of drug
        # nlp = spacy.blank("en")
        doc = nlp(text_before_medicine)
        drug_name_set = set()
        for ent in doc.ents:
            if ent.label_ == "CHEMICAL":
                drug_name_set.add(ent.text)
        if "COVID" in cleaned_comments and "19" in cleaned_comments:
            print("YES")
            drug_name_set.add("COVID-19")
        drug_name_list = list(drug_name_set)
        drug_name_string = ','.join(drug_name_list)
        print("LLT", drug_name_string)

        # Indication
        indication_keywords = ["noticed", "observed", "experienced", "suffered", "reported", "developed", "showed",
                               "encountered"]

        text_for_indication = ""
        lines = text_before_medicine.split("\n")
        for i, line in enumerate(lines):
            for indication_keyword in indication_keywords:
                if indication_keyword in line:
                    start_line = line.find(indication_keyword)
                    text_for_indication = line[start_line:]

                    # end_line = death_text.find('.')
                    # death_comments = death_text[:end_line]
        indication_text += text_for_indication + "\n"

        doc = nlp(indication_text)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                llt_indicators.append(ent.text)
        llt_indicators_string = ','.join(llt_indicators)
        print("Indication LLT:", llt_indicators)
        print("Indication Comment:", indication_text)

        # Reaction after drug

        doc = nlp(text_after_medicine)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                llt_reactions.append(ent.text)
        llt_reactions_string = ','.join(llt_reactions)
        print("Reaction LLT:", llt_reactions)
        print("Reaction Comment:", text_after_medicine.split("/n")[:2])
    else:
        print("First name:", mother_first_name)
        print("Middle name:", mother_middle_name)
        print("Last name:", mother_last_name)
        print("Initials", initials)
        print("LLT:", mother_llt)
        print("Age:", mother_age)
        print("Time unit:", time_unit)
        print("Date of Birth;", dob)
        print("Sex:", "")
        print("Ethnic Group:", group)
        print("Height in (cm):", height_in_cm)
        print("Weight (kg):", weight)
        print("LMP:", lmp)
        print("Gestation period:", gestation_period)
        print("Start date:", start_date)
        print("End date:", end_date)
        print("Continuing", continuing)
        print("LLT:", llt)
        print("Comments:", comments)
        print("LLT Indicators:", llt_indicators)
        print("Comments:", indication_text)
        print("Name of Drug:", drug_name)
        print("Drug LLT:", llt_reactions)
        print("Comments:", reaction_comment)

    parent = {
        "parent_information": {
            "protect_confidentiality": "Yes",
            "title": "",
            "first_name": mother_first_name,
            "middle_name": mother_middle_name,
            "last_name": mother_last_name,
            "initials": "",
            "age_of_parent": mother_age,
            "age_unit": time_unit,
            "date_of_birth": dob,
            "sex": sex,
            "ethnic_group": ethnic,
            "weight": weight,
            "height": height_in_cm,
            "parent_breastfeeding": "",
            "last_menstrual_period": lmp,
            "comments": cleaned_comments
        },
        "parent_medical_history": {
            "parent_history": cleaned_comments,
            "disease_surgical_procedure": "",
            "meddra_version": "",
            "start_date": start_date,
            "end_date": end_date,
            "continuing": continuing,
            "llt": mother_llt,
            "comments": cleaned_comments
        },
        "parent_past_drug_history": {
            "name_of_drug": drug_name,
            "active_or_molecules": drug_name,
            "start_date": "",
            "end_date": "",
            "llt_indication": llt_indicators_string,
            "llt_indication_medracode": "",
            "llt_indication_version": "",
            "llt_reaction": llt_reactions_string,
            "llt_reaction_medracode": "",
            "llt_reaction_version": "",
            "comments": cleaned_comments
        }
    }

    return parent



