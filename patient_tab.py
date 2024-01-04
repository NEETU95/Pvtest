from PyPDF2 import PdfReader
import os
import spacy
import re
import pycountry
import json
import pandas as pd
#from parent import mother_llt, all_text, nlp, nlp_1



def get_patient_text(source_text, en_core, bcd5r):
    all_text = source_text
    nlp_1 = en_core
    nlp = bcd5r
    # Title
    title = ""
    protect_confidentiality = "Yes"
    print("Title:", title)

    report_to_discussion = ""
    first_three_lines = ""
    case_keywords = ["Case Presentation", "Case Summary", "Case History", "Case description", "Case Report"]
    found_case_type = None
    text_after_case_type = ""
    doc = nlp_1(all_text)
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
        end_line = -1
        for i, line in enumerate(all_text.split('\n')):
            if search_term in line:
                count += 1
                found_start_line = i  # Assuming you want to store the line index where "Case Report" is found
            if "Discussion" in line:
                end_line = i
        print("count is", count)
        if count > 0 and found_start_line != -1:
            # Extract the found line and the subsequent 7 lines
            extracted_lines = all_text.split('\n')[found_start_line:end_line]
            report_to_discussion = '\n'.join(extracted_lines)
            first_three_lines_split = report_to_discussion.split("\n")[:10]
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

    doc = nlp_1(first_three_lines)

    # First Name
    title = ""
    patient_name = ""
    first_name = ""
    middle_name = ""
    last_name = ""
    current_name = ""
    for token in doc:
        if token.ent_type_ == "PERSON":
            current_name += token.text + " "
        else:
            if current_name.strip():
                patient_name += current_name.strip() + " "
                current_name = ""

    # Handle the last name if present
    if current_name.strip():
        patient_name += current_name.strip()

    # Remove duplicate names
    patient_name = ' '.join(list(dict.fromkeys(patient_name.split())))
    print(patient_name)
    name_parts = patient_name.split()
    num_words = len(name_parts)
    if num_words == 2:
        # If the author name has only 2 words, consider them as first and last names
        first_name = name_parts[0]
        last_name = name_parts[1]
    elif num_words == 0:
        first_name = "Unk"
    elif num_words == 1:
        first_name = name_parts[0]
    elif num_words >= 3:
        first_name = name_parts[0]
        middle_name = name_parts[1]
        last_name = " ".join(name_parts[2:])

    print("First name:", first_name)
    print("Middle name:", middle_name)
    print("Last name:", last_name)

    # Initials
    initials = ""
    if first_name == 'Unk':
        initials = 'Unk'
    elif not last_name:
        initials = first_name[0]
    else:
        initials = first_name[0] + last_name[0]
    print("Initials:", initials)

    # OCCUPATION
    occupation = ""
    print("Occupation", occupation)

    # Medical record source type
    medical_record_source_type_keywords = ["GP", "Specialist", "Hospital Record", "Investigation", "gpmrn",
                                           "specialistMrn", "hospitalMrn", "investigation"]
    medical_record_source_type = ""
    print("Medical record source type:", medical_record_source_type)

    # Medical record number
    medical_record_number = ""
    print("Medical Record number:", medical_record_number)

    # Age
    age = ""
    time_unit = ""
    time_units = ["year", "day", "decade", "month", "hour", "weeks"]

    # Regular expression pattern to match age information with hyphen and different time units
    pattern = r'(\d+)\s*-?\s*(' + '|'.join(time_units) + ')'
    age_pattern = re.compile(pattern)
    matches = age_pattern.findall(first_three_lines)
    if matches:
        ages, time_unit_ = int(matches[0][0]), matches[0][1]
        match_index = first_three_lines.find(matches[0][1], first_three_lines.find(matches[0][0]))
        if match_index != -1 and first_three_lines.find("old", match_index) != -1:
            age = ages
            time_unit = time_unit_
    print("Age at time of onset of reaction:", age)

    # Extract units
    print("Age at time of onset of reaction(units):", time_unit)

    # Date of birth
    date_of_birth = ""
    if "born" in first_three_lines.split(" "):
        dob_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
        matches = dob_pattern.findall(first_three_lines)
        if matches:
            date_of_birth = matches[0]
    print("Date of birth:", date_of_birth)

    # Age group
    age_groups = ['Foetus', 'Neonate', 'Infants', 'Child', 'Adolescent', 'Adults', 'Elderly']

    age_group = ""
    if age:
        if (0 <= age <= 12 and time_unit == time_units[3]) or (1 <= age <= 50 and time_unit == time_units[5]) or (
                time_unit == time_units[4]):
            age_group = age_groups[1]
            print("Age group:", age_groups[1])
        elif (1 <= age <= 3 and time_unit == time_units[0]) or (13 <= age <= 36 and time_unit == time_units[3]):
            print("Age group:", age_groups[2])
            age_group = age_groups[2]
        elif 3 <= age <= 11 and time_unit == time_units[0]:
            print("Age group:", age_groups[3])
            age_group = age_groups[3]
        elif 12 <= age <= 18 and time_unit == time_units[0]:
            print("Age group:", age_groups[4])
            age_group = age_groups[4]
        elif (19 <= age <= 69 and time_unit == time_units[0]) or (3 <= age <= 6 and time_unit == time_units[2]):
            print("Age group:", age_groups[5])
            age_group = age_groups[5]
        elif (age > 69 and time_unit == time_units[0]) or (7 <= age < 10 and time_unit == time_units[2]):
            print("Age group:", age_groups[6])
            age_group = age_groups[6]
        else:
            print("Age group:", age_groups[0])
            age_group = age_groups[0]

    # Sex
    patient_gender = ["Male", "Female", "Unknown"]

    sex = ""
    for token in doc:
        if token.text.lower() in ["male", "he", "his", "young man", "gentleman", "man", "boy"]:
            sex = patient_gender[0]
            break
        elif token.text.lower() in ["female", "she", "her", "young woman", "woman", "girl"]:
            sex = patient_gender[1]
            break
        else:
            sex = patient_gender[2]
    print("Sex:", sex)

    if sex == patient_gender[2]:
        initials = "UNK"
    # GROUP OF PATIENT
    ethnic_group = ""
    ethnic = ""
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
    for i in groups:
        if i in first_three_lines.split(" "):
            ethnic_group = i
    if ethnic_group == "African American":
        ethnic = ethnic_groups[0]
    elif ethnic_group == "American Indian" or ethnic_group == "Alaska Native":
        ethnic = ethnic_groups[1]
    elif ethnic_group == "Asian":
        ethnic = ethnic_groups[2]
    elif ethnic_group == "Black":
        ethnic = ethnic_groups[3]
    elif ethnic_group == "Caucasian":
        ethnic = ethnic_groups[4]
    elif ethnic_group == "Native Hawaiian" or ethnic_group == "Other Pacific":
        ethnic = ethnic_groups[5]
    elif ethnic_group == "White":
        ethnic = ethnic_groups[7]
    print("Ethnic_group:", ethnic)

    # Weight
    weight = ""
    units = " "

    # Regular expression pattern to match weights with various units
    weight_pattern = re.compile(r'(\d+(\.\d+)?)\s*(kgs?|grams?|g|Kilo\s*grams?)', re.IGNORECASE)

    # Find all matches in the text
    matches = weight_pattern.findall(first_three_lines)
    sentence = ""
    # Extract weights and units if matches are found
    for match in matches:
        weight, _, units = match
        sentence_start = max(0, first_three_lines.rfind('.', 0, match.start()))
        sentence_end = first_three_lines.find('.', match.end())
        sentence = first_three_lines[sentence_start:sentence_end].strip()

    if any(word in sentence.lower() for word in ['weigh']):
        if units in ["g", "grams"]:
            converted_weight = int(weight) / 1000
            weight = converted_weight
        elif units.lower() in ["lbs", "pounds"]:
            # Convert pounds to kilograms (1 lb = 0.453592 kg)
            converted_weight = int(weight) * 0.453592
            weight = converted_weight
        else:
            weight = weight
    print("Weight (kg):", weight)

    # Height
    height = ""
    inches = ""
    height_in_cm = ""
    # Regular expression pattern to match heights in various units
    height_pattern = re.compile(r'(\d+)\s*(cm|centimeters|feet|ft)\s*(\d+)?\s*(inches)?', re.IGNORECASE)

    # Find all matches in the text
    matches = height_pattern.finditer(first_three_lines)

    # Extract heights and units if matches are found
    for match in matches:
        height, units, inches, _ = match.groups()
        # Find the entire sentence containing the height information
        sentence_start = max(0, first_three_lines.rfind('.', 0, match.start()))
        sentence_end = first_three_lines.find('.', match.end())
        sentence = first_three_lines[sentence_start:sentence_end].strip()

    if any(word in sentence.lower() for word in ['height', 'tall']):
        if units.lower() in ['feet', 'ft']:
            height_in_cm = int(height) * 30.48  # Convert feet to cm
            if inches:
                height_in_cm += int(inches) * 2.54  # Convert inches to cm
            print("Height (cm):", height_in_cm)
        else:
            height_in_cm = height
            print("Height (cm):", height_in_cm)
    else:
        print("Height (cm):", height_in_cm)

    # Opening Female section
    # LMP
    last_menstrual_period = ""
    pregnant = ['Yes', 'No', 'Unknown']

    edd = ""
    pregnant_ = ""
    gestation_period = ""
    gestation_period_units = ""
    pregnant_at_time_of_vaccination = ['Yes', 'No']
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
                    last_menstrual_period = date_match.group(1)
        print("Last Menstrual period", last_menstrual_period)

        # pregnant or not
        if 'not pregnant' in first_three_lines.lower():
            pregnant_ = pregnant[1]

        elif 'pregnant' in first_three_lines.lower() and "not pregnant" not in first_three_lines:
            pregnant_ = pregnant[0]
        else:
            pregnant_ = pregnant[2]
        print("pregnant:", pregnant_)

        # Pregnant information extraction after confirms
        if pregnant_ == "Yes":

            for word in estimation_delivery_date:
                if word in first_three_lines.lower():
                    sentence_start = max(0, first_three_lines.rfind('.', 0, first_three_lines.lower().find(word)))
                    sentence_end = first_three_lines.find('.', first_three_lines.lower().find(word))
                    sentence = first_three_lines[sentence_start:sentence_end].strip()
                    print(f"EDD Word '{word}' related to estimation delivery date found in the text.")
                    print(f"EDD Sentence: '{sentence}'")

                    date_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
                    date_match = date_pattern.search(sentence)
                    if date_match:
                        edd = date_match.group(1)
                    else:
                        date_pattern = re.compile(r'\b(\w+ \d{1,2}, \d{4})\b')

                        # Search for the date pattern in the text
                        date_match = date_pattern.search(first_three_lines)

                        # Extract and print the date if found
                        if date_match:
                            edd = date_match.group(1)
            print("Estimation delivery date", edd)

            # OUTCOME OF PREGNANCY
            outcome_of_pregnancy = [
                "Congrnital abnormality",
                "Live birth at term",
                "Other medically Significant",
                "Premature delivery",
                "Spontaneous abortion",
                "Still born",
                "Still born Unknown"
            ]

            # Gestation period

            gestation_period_unit = ["Trimester", "Day", "Month", "Week"]

            # Regular expression pattern to match age information with hyphen and different time units
            pattern = r'(\d+)\s*-?\s*(' + '|'.join(gestation_period_unit) + ')'
            gestation_period_pattern = re.compile(pattern)
            matches = gestation_period_pattern.findall(first_three_lines)
            if matches:
                gestation_period, gestation_period_units = int(matches[0][0]), matches[0][1]
            print("Gestation period::", gestation_period)
            print("Gestation period units:", gestation_period_units)

            concomitant_therapy_administered = ['true', 'false']
            breastfeeding = ['true', 'false']

    # ADDRESS EXTRACTION
    found_patient_countries = ""
    city_ = ""
    is_part_of_city = False
    city = ""
    address = ""
    affiliations = first_three_lines.split("\n")
    # List of keywords indicating country information
    country_keywords = ["resides", " is from", "country"]
    # Loop through affiliations and search for country names and cities
    for affiliation in affiliations:
        for keyword in country_keywords:
            if keyword in affiliation:
                country_found = False  # Flag to indicate if a country has been found in this affiliation
                deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan', 'MACAU',
                                     'Republic Of Ireland',
                                     'USA']
                for i in deleted_countries:
                    if i in affiliation:
                        found_patient_countries.append(i)
                        country_found = True
                        break

                for country in pycountry.countries:
                    if country.name in affiliation and not found_patient_countries:
                        found_patient_countries = country.name
                        country_found = True
                        break  # Stop searching for country names in this affiliation
                country_doc = nlp(affiliation)
                for token in country_doc:
                    if token.ent_type_ == "GPE" and token.text:
                        city = token.text

    # If the city string isn't finished at the end
    if city != found_patient_countries:
        city_ = city

    # city
    print("Patient City:", city_)

    # State
    state = " "
    print("Patient state:", state)

    # Pincode
    pincode = " "
    json_file = "postal-codes.json"
    with open(json_file, encoding='utf-8-sig') as file:
        country_regexes = json.load(file)
    pin_codes = []

    # Get the text before the first period in the first split
    desired_text = first_three_lines
    for country_data in country_regexes:
        regex_pattern = country_data["Regex"]
        modified_pattern = r"\b" + re.sub(r'^\^|\$$', '', regex_pattern) + r"\b"

        matches = re.finditer(modified_pattern, desired_text)
        for match in matches:
            # Get the starting and ending positions of the match
            match_start = match.start()
            match_end = match.end()

            # Find the sentence start and end positions
            sentence_start = max(0, desired_text.rfind('.', 0, match_start))
            sentence_end = desired_text.find('.', match_end)

            # Extract the sentence and strip leading/trailing whitespaces
            sentence = desired_text[sentence_start:sentence_end].strip()
            if found_patient_countries and found_patient_countries[0] in sentence:
                pin_codes.append(match.group())

    max_digit_count = 0
    string_with_max_digits = ''

    for string in pin_codes:
        digit_count = sum(c.isdigit() for c in string)  # Count the number of digits in the string
        if digit_count > max_digit_count:
            max_digit_count = digit_count
            pincode = string
    print("Patient Pincode:", pincode)

    # Print the found countries
    print("Patient Country:", found_patient_countries)

    # Phone number
    lines = first_three_lines.split('\n')

    # Variable to store the extracted phone numbers
    phone_number = ""

    # Find the line containing 'Fax' or 'Tel' and extract text after that
    for line in lines:
        if 'Fax' in line or 'Tel' in line or '+' in line or 'Phone' in line:
            # Extract the text after 'Fax' or 'Tel'
            # extracted_text = line.split('Fax:')[-1].strip() if 'Fax' in line else line.split('Tel:')[-1].strip()
            extracted_text = line

            # Extract numbers with the '+' character
            numbers_with_plus = re.findall(r'\+\d[\d -]+', extracted_text)
            numbers_with_plus_in_brackets = re.findall(r'\(\+\d+\)-\d+', line)
            numbers_with_plus_in_brackets_and_space = re.findall(r'\(\+\d+\) \d+', line)
            if numbers_with_plus:
                phone_number = numbers_with_plus
            elif numbers_with_plus_in_brackets:
                phone_number = numbers_with_plus_in_brackets
            elif numbers_with_plus_in_brackets_and_space:
                phone_number = numbers_with_plus_in_brackets_and_space

    print("Patient PhoneNumber", phone_number)

    # Email pattern
    email_address = " "
    email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'
    # Find email addresses in the text
    patient_email = re.findall(email_pattern, first_three_lines)
    if patient_email:
        email_address = patient_email
    print("Patient Email Address:", email_address)

    relevant_medical_history_and_concurrent = ""

    # Medical History
    # Starting date
    start_date = ""
    end_date = ""
    history_keywords = ["medical history", "history", "he had", "she had", "diagnosed", "suffered"]
    for i, line in enumerate(lines[:-2]):
        for keyword in history_keywords:
            if keyword in line:
                if i + 1 < len(lines):
                    extracted_text = line
                    extracted_next_text = lines[i + 1]
                    extracted_for_end_date = lines[i + 2]
                    pattern = re.compile(
                        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
                    )
                    match = re.search(pattern, extracted_text)
                    if match:
                        matched_date = match.group()
                        start_date = matched_date
                    else:
                        match_2 = re.search(pattern, extracted_next_text)
                        if match_2:
                            matched_date_2 = match_2.group()
                            start_date = matched_date_2
                    match_end = re.search(pattern, extracted_next_text)
                    if match_end:
                        matched_end_date = match_end.group()
                        if matched_end_date != start_date:
                            end_date = matched_end_date
                        else:
                            match_end_2 = re.search(pattern, extracted_for_end_date)
                            if match_end_2:
                                matched_date_2 = match_end_2.group()
                                end_date = matched_date_2

    print("Start date:", start_date)
    print("End date:", end_date)

    # Continuing
    continuing = ""
    continuing_list = ['true', 'false', 'null']

    if end_date:
        continuing = continuing_list[1]
    for i, line in enumerate(lines):
        for keyword in history_keywords:
            if keyword in line:
                # Check if there is a next line
                if i + 1 < len(lines):
                    extracted_text = line[i:]
                    if "continu" in extracted_text.lower():
                        continuing = continuing_list[0]
                    else:
                        continuing = continuing_list[2]

    print("Continuing:", continuing)

    family_history = ["True", "False"]

    # Case of Death
    dead_keywords = ["expired", "died", "dead", "passed away", "demise", "murdered", "lost life"]
    death_comments = ""
    text = ""
    death_text = ""
    dod = ""
    lines = report_to_discussion.split("/n")
    for i, line in enumerate(lines):
        for keyword in dead_keywords:
            if keyword in line:
                start_line = line.find(keyword)
                text = line[start_line:]
    death_text += text + "\n"
    # end_line = death_text.find('.')
    # death_comments = death_text[:end_line]
    dod_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
    matches = dod_pattern.findall(death_text)
    if matches:
        dob = matches[0]
    print("Date of death:", dod)

    # Cause of death
    cause_of_death = []
    death_llt = []
    doc = nlp(death_text)
    for ent in doc.ents:
        if ent.label_ == "DISEASE" and ent.text not in dead_keywords:
            cause_of_death.append(ent.text)
            death_llt.append(ent.text)
    death_llt_string = ','.join(death_llt)
    cause_of_death_string = ','.join(cause_of_death)
    print("Cause of death", cause_of_death_string)
    print("LLT", death_llt_string)
    cause_of_death_comments = death_llt
    print("Comments", death_text)
    # AUTOPSY PART
    autopsy_keywords = ["autopsy", "Post-mortem", "necropsy", "examination", "medical examination", "post mortem"]
    autopsy_done = ["true", "false", "UNk", "ASKU"]

    text_after_autopsy = " "
    autopsy_text = ""
    autopsy = ""
    lines = death_text.split("\n")
    for i, line in enumerate(lines):
        for keyword in autopsy_keywords:
            if keyword in line:
                autopsy = autopsy_done[0]
                start_line = line.find(keyword)
                text_after_autopsy = line[start_line:]

                # end_line = death_text.find('.')
                # death_comments = death_text[:end_line]
            elif keyword in line and "no" in line or "not" in line:
                autopsy = autopsy_done[1]
            else:
                autopsy = autopsy_done[2]
    autopsy_text += text_after_autopsy + "\n"
    print("Autopsy:", autopsy)
    autopsy_cause_of_death = []
    autopsy_llt = []
    doc = nlp(autopsy_text)
    for ent in doc.ents:
        if ent.label_ == "DISEASE" and ent.text not in dead_keywords:
            autopsy_cause_of_death.append(ent.text)
            autopsy_llt.append(ent.text)
    if "COVID" in autopsy_text:
        autopsy_cause_of_death.append("COVID-19")
        autopsy_llt.append("COVID-19")
    autopsy_llt_string = ', '.join(autopsy_llt)
    autopsy_cause_of_death_string = ', '.join(autopsy_cause_of_death)
    print("Cause of death", autopsy_cause_of_death_string)
    print("LLT", autopsy_llt_string)
    print("Autopsy Comments", autopsy_text)

    # Drug details
    # med7 = spacy.load("en_core_med7_lg")

    text_line = ""
    previous_lines = []
    text_before_medicine = ""
    text_after_medicine = ""
    products = pd.read_excel("product_names.xlsx")
    for line_number, line in enumerate(report_to_discussion.split('\n')):
        for drug in products['product_name']:
            if drug.lower() in line.lower():
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

    medical_history_text = text_before_medicine

    # Process the text using the loaded model
    doc = nlp(text_before_medicine)

    # Access entities in the processed document
    drugs = set()
    for ent in doc.ents:
        if ent.label_ == "CHEMICAL":
            drugs.add(ent.text)
            print("drugs are:", ent.text)
    drugs_list = list(drugs)
    drugs_string = ', '.join(drugs_list)

    llt_medical = []
    # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None, use_gpu=False)

    for ent in doc.ents:
        if ent.label_ == "DISEASE":
            llt_medical.append(ent.text)
    print("Indication LLT:", llt_medical)
    print("Indication Comment:", text_before_medicine)

    filtered_llt = llt_medical

    llt_medical_string = ', '.join(filtered_llt)

    # Indication
    indication_keywords = ["noticed", "observed", "experienced", "suffered", "reported", "developed", "showed",
                           "encountered", "treat"]
    text_for_indication = ""
    lines = text_before_medicine.split('\n')[-5:]
    indication_text = '\n'.join(lines)
    # for i, line in enumerate(lines):
    #     for keyword in indication_keywords:
    #         if keyword in line:
    #             start_line = line.find(keyword)
    #             text_for_indication = line[start_line:]
    #
    #             # end_line = death_text.find('.')
    #             # death_comments = death_text[:end_line]
    # indication_text += text_for_indication + "\n"
    llt_indicators = []
    # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None, use_gpu=False)
    doc = nlp(indication_text)
    for ent in doc.ents:
        if ent.label_ == "DISEASE":
            llt_indicators.append(ent.text)
    llt_indicators_string = ','.join(llt_indicators)
    print("Indication LLT:", llt_indicators)
    print("Indication Comment:", indication_text)

    if llt_indicators:
        llt_1 = [item for item in llt_medical if item not in llt_indicators]
        llt = ','.join(llt_1)
    else:
        llt = filtered_llt

    # start and end of drugs
    start_date_drug = ""
    end_date_drug = ""
    pattern = re.compile(
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    )
    match = re.search(pattern, indication_text)
    if match:
        matched_date = match.group()
        start_date_drug = matched_date
    match_end = re.search(pattern, indication_text)
    if match_end:
        matched_end_date = match_end.group()
        if matched_end_date != start_date:
            end_date_drug = matched_end_date

    # Reaction after drug
    llt_reactions = []
    doc = nlp(text_after_medicine)
    for ent in doc.ents:
        if ent.label_ == "DISEASE":
            llt_reactions.append(ent.text)
    print("Reaction LLT:", llt_reactions)
    llt_reactions_string = ', '.join(llt_reactions)
    comment_reactions = text_after_medicine
    print("Reaction Comment:", comment_reactions)

    patient = {
        "patient_information": {
            "parent_child_foetus_case": "",
            "protect_confidentiality": protect_confidentiality,
            "title": title,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "initials": initials,
            "occupation": occupation,
            "medical_record_source_type": medical_record_source_type,
            "medical_record_number": medical_record_number,
            "age_at_time_of_onset_of_reaction": age,
            "age_at_time_of_onset_of_reaction_units": time_unit,
            "date_of_birth": date_of_birth,
            "age_group": age_group,
            "sex": sex,
            "ethnic_group": ethnic,
            "weight": weight,
            "height": height_in_cm,
            "last_menstrual_period": last_menstrual_period,
            "pregnant": pregnant_,
            "expected_delivery_date": edd,
            "outcome_of_pregnancy": "",
            "gestation_period_when_reaction_was_observed_in_foetus": gestation_period,
            "gestation_period_units": gestation_period_units,
            "concomitant_therapy_administered": "",
            "breastfeeding": "",
            "pregnant_at_time_of_vaccination": "",
            "military_status": "",
            "address_1": address,
            "address_2": "",
            "city": city_,
            "state_or_province": "",
            "pincode": pincode,
            "country": found_patient_countries,
            "phone_number": phone_number,
            "email_address": email_address,
            "relevant_medical_history_and_concurrent_conditions": relevant_medical_history_and_concurrent
        },
        "medical_history": {
            "disease_surgical_procedure": "",
            "meddra_version": "",
            "start_date": start_date,
            "end_date": end_date,
            "continuing": continuing,
            "llt": llt_medical,
            "comments": medical_history_text,
            "family_history": ""
        },
        "past_drug_history": {
            "name_of_drug": drugs_list,
            "active_or_molecules": drugs_string,
            "start_date": start_date_drug,
            "end_date": end_date_drug,
            "llt_indication": llt_indicators,
            "llt_indication_medracode": "",
            "llt_indication_version": "",
            "llt_reaction": llt_reactions,
            "llt_reaction_medracode": "",
            "llt_reaction_version": "",
            "comments": comment_reactions,
            "condition_type": "",
            "verbatim": ""
        },
        "case_death": {
            "date_of_death": dod,
            "cause_of_death": cause_of_death_string,
            "llt_case_of_death": death_llt_string,
            "medra_code": "",
            "medra_version": "",
            "comment": death_text,
            "was_autopsy_done": autopsy,
            "autopsy_cause_of_death": autopsy_cause_of_death_string,
            "llt_autopsy": autopsy_llt_string,
            "auto_spy_medra_code": "",
            "auto_spy_medra_version": ""

        }
    }
    return patient