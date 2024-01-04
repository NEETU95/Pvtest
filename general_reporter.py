from PyPDF2 import PdfReader
import spacy
import re
import pandas as pd
import pycountry
import json
from fastapi import HTTPException
from metapub import PubMedFetcher

# weekly_reader = PdfReader('36cd8337-0986-4503-bada-61151a2da12a_Weekly literature Hits PDF-sosa.pdf')
# source_file_reader = PdfReader('Sosa NH..pdf')
# # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
# weekly_reader_num_pages = len(weekly_reader.pages)
#
# source_file_num_pages = len(source_file_reader.pages)
# weekly_text = ""
# all_text = ""
# nlp = spacy.load("en_core_web_sm")
# nlp_1 = spacy.load("en_ner_bc5cdr_md")
# # Loop through all pages and extract text
# for page_num in range(source_file_num_pages):
#     page = source_file_reader.pages[page_num]
#     text = page.extract_text()
#     all_text += text
# for page_num in range(weekly_reader_num_pages):
#     page = weekly_reader.pages[page_num]
#     text = page.extract_text()
#     weekly_text += text
# meta = source_file_reader.metadata

def get_general_reporter(source_text, en_core, weekly_text_1, meta_data):
    try:
        all_text = source_text
        nlp = en_core
        pmid_pattern = re.compile(r'\b\d{8}\b')  # Assumes PMIDs are 8-digit numbers

        # Search for PMIDs in the PDF text
        matches = re.findall(pmid_pattern, all_text)
        if matches:
            print(matches)
        # weekly_reader = PdfReader("Weekly literature Hits PDF-sosa.pdf")
        # # Get the number of pages in the PDF
        # weekly_num_pages = len(weekly_reader.pages)

        # Initialize an empty string to store the extracted text
        weekly_text = weekly_text_1

        # # Loop through all pages and extract text
        # for page_num in range(weekly_num_pages):
        #     page = weekly_reader.pages[page_num]
        #     text = page.extract_text()
        #     weekly_text += text

        # print("weekly text is", weekly_text)

        ###############################################

        # Finding author name using title
        meta = meta_data
        weekly_doc = nlp(weekly_text)
        doc = nlp(all_text)
        title_of_page = meta.title
        print("title", title_of_page)

        title_from_literature = ""
        author_name = " "
        extracted_text = ""
        text_lines = ""
        doi = ""
        literature_reference = ""
        year = ""
        author = ""
        digital_object_identifier = ""
        literature_title = ""
        vol = ""
        journal = ""
        pages = ""
        if not title_of_page:
            text_up_to_doi_for_author = ""
            # Iterate through the lines
            for line in all_text.split("\n"):
                for line in all_text.split("\n"):
                    if "DOI:" in line or "doi:" in line:
                        text_up_to_doi_for_author = line
                        break  # Stop when the line containing "DOI:" is found
                affiliations = text_up_to_doi_for_author.split("\n")
                index_doi = text_up_to_doi_for_author.find('DOI:')
                doi_raw = text_up_to_doi_for_author[index_doi + len('doi:'):].strip()
                doi = re.sub(r'[^\x00-\x7F]+', '', doi_raw)
            print("doi", doi)
            if not doi:
                raise HTTPException(status_code=11, detail="DOI not found from source document")
            else:
                try:
                    fetch = PubMedFetcher()
                    article = fetch.article_by_doi(doi)
                    title_of_page = article.title
                    author = article.authors[0]
                    digital_object_identifier = doi
                    literature_reference = article.citation
                    vol = article.volume
                    year = article.year
                    journal = article.journal
                    page = article.pages
                    if page and not any(char.isalpha() for char in page):
                        pages = page

                except Exception as e:
                    print('Error! Code: {c}, Message, {m}'.format(c=type(e).__name__, m=str(e)))
                # except Exception as e:
            #     raise HTTPException(status_code=e.sta, detail="Error raised from selenium browser")
        print('1')


        # getting title from literature
        print('6')
        if title_of_page:
            print('7')
            print('title is', title_of_page)
            if title_of_page.split()[0] and title_of_page.split()[1] and title_of_page.split()[2] in weekly_doc.text:
                weekly_split = weekly_text.split('\n')
                print('8')
                # print(weekly_split)
                for i, line in enumerate(weekly_split):
                    print(line)
                    if (
                            title_of_page.split()[0] in line
                            and
                            title_of_page.split()[1] in line
                            and
                            title_of_page.split()[3] in line
                            and
                            title_of_page.split()[4] in line
                    ):
                        line_index = i
                        print('line_index', line_index)
                        extracted_text = '\n'.join(weekly_split[line_index + 1:])
                        print('extracted_text', extracted_text)
                        print('10')
                        break
                # word_to_find = title_of_page.split()[-1]
                #
                # word_index = weekly_text.find(title_of_page.split()[3])
                # # Extract text after the specific word
                # extracted_text = weekly_doc.text[word_index + len(title_of_page.split()[0]):]
                # text_after_title = weekly_text.split(title_of_page.split()[-1], 1)[-1]
                # Sample text split into lines
                text_lines = extracted_text.split('\n')
                print(text_lines)
                # Initialize variables to capture the author and their name
                author_line = None
                text_up_to_affiliations = ""
                print('9')
                for line in text_lines:
                    if "Affiliations" in line:
                        break  # Stop when the line containing "DOI:" is found
                    text_up_to_affiliations += line
                print('text_up_to', text_up_to_affiliations)
                affiliations = text_up_to_affiliations.split("\n")
                print(affiliations)
                # Extract text between "Authors" and the first occurrence of "1" after "Affiliations"
                match = re.search(r'Authors([\s\S]*?)\b1\b', text_up_to_affiliations)
                if match:
                    author_name_before_1 = match.group(1).strip()
                    if ',' in author_name_before_1:
                        first_author_name = author_name_before_1.split(',')[1]
                        author_name = re.sub(r'\d', '', first_author_name)
                        print(author_name)
                    else:
                        first_author_name = author_name_before_1
                        author_name = re.sub(r'\d', '', first_author_name)
                        print(author_name)
                print('10')

                # for i, line in enumerate(text_lines):
                #     if "Author" in line or "Authors" in line:
                #         author_line = line
                #         print(author_line)
                #         match = re.match(r'^(.*?1)\s*,?\s*(.*)$', text_lines[i + 1])
                #
                #         if i + 1 < len(text_lines):
                #             # Using regular expression to extract author name before "1" and the part after the comma
                #             match = re.match(r'^(.*?1)\s*,?\s*(.*)$', text_lines[i + 1])
                #
                #             if match:
                #                 author_name_before_1 = match.group(1).strip()
                #                 if ',' in author_name_before_1:
                #                     first_author_name = author_name_before_1.split(',')[1]
                #                     author_name = re.split(r'\d', first_author_name)[0].strip()
                #                     break
                #                 else:
                #                     first_author_name = author_name_before_1
                #                     author_name = re.split(r'\d', first_author_name)[0].strip()
                #                     break

            # General tab
            print("###### General #######")
            general_information = {
                "type_of_report": "Other(Literature)",
                "initial_receipt_date": "",
                "latest_receipt_date": "",
                "country": "",
                "medically_confirmation": "Yes",
                "expedited_report": "",
                "first_sender": "Other",
                "report_nullification_or_amendment": "",
                "reason_for_nullification_or_amendment": ""

            }

            type_of_report = "Other(Literature)"
            print("Type of report:", type_of_report)

            # Initial receipt date
            weekly_doc = nlp(weekly_text)
            initial_receipt_date = ""
            sent_line = ''
            for line in weekly_text.split('\n'):
                if 'Sent on' in line:
                    sent_line = line
                    break

            if sent_line:
                # Split the line at the comma and get text after the comma
                split_text = sent_line.split(',')
                if len(split_text) > 1:
                    text_after_comma = split_text[1].strip()
                    parsed_date = pd.to_datetime(text_after_comma, format='%Y %B %d')
                    # Format the date in the desired format
                    general_information["initial_receipt_date"] = parsed_date.strftime('%d/%m/%Y')

                    print("Initial Receipt Date:", general_information["initial_receipt_date"])
                else:
                    print("can't change date")

            else:
                print("No 'Sent on' line found in the text.")

            # Latest receipt date
            general_information["latest_receipt_date"] = general_information["initial_receipt_date"]
            if not general_information["initial_receipt_date"]:
                raise HTTPException(status_code=2, detail="Latest Receipt date is not found from weekly literature")
            # print("Latest Receipt date:", initial_receipt_date)

            # country
            found_countries = ""
            found_cities = []
            text_up_to_doi = ""
            is_part_of_city = False
            city = ""
            if author_name.lower() in weekly_doc.text.lower():
                print('author_name',author_name.lower())
                print('11')
                # Find the index of the specific word
                word_index = weekly_doc.text.find(author_name)

                # Extract text after the specific word
                extracted_text = weekly_doc.text[word_index + len(author_name):]
                # Iterate through the lines
                for line in extracted_text.split("\n"):
                    print('line is', line)
                    print('12')
                    if "DOI:" in line or "doi" in line:
                        break  # Stop when the line containing "DOI:" is found
                    text_up_to_doi += line
                    print("text upto doi",text_up_to_doi)
                affiliations = text_up_to_doi.split("\n")
                # Loop through affiliations and search for country names and cities
                for affiliation in affiliations:
                    country_found = False  # Flag to indicate if a country has been found in this affiliation
                    deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan', 'MACAU',
                                         'Republic Of Ireland',
                                         'USA']
                    for i in deleted_countries:
                        if i in affiliation:
                            found_countries = i
                            country_found = True
                            break

                    for country in pycountry.countries:
                        if country.name in affiliation and not found_countries:
                            found_countries = country.name
                            country_found = True
                            break  # Stop searching for country names in this affiliation
                    country_doc = nlp(affiliation)
                    for token in country_doc:
                        if token.ent_type_ == "GPE" and token.text:
                            if not is_part_of_city:
                                is_part_of_city = True
                                city = token.text
                            else:
                                city += " " + token.text
                        else:
                            if is_part_of_city:
                                found_cities.append(city)
                                is_part_of_city = False
                                city = ""
                countries = " "
                # If the city string isn't finished at the end
                if is_part_of_city != found_countries:
                    found_cities.append(city)

                general_information["country"] = found_countries
                if not general_information["country"]:
                    raise HTTPException(status_code=1, detail="Country is not found from weekly literature")

                # def get_country_by_state(state_name):
                #     for subdivision in pycountry.subdivisions:
                #         # Check if the state name is a substring of the subdivision name
                #         if state_name.lower() in subdivision.name.lower():
                #             # Get the country using the alpha-2 code of the subdivision
                #             country_from_search = pycountry.countries.get(alpha_2=subdivision.country_code)
                #             return country_from_search.name
                #
                # if found_cities and not found_countries:
                #     country_name = get_country_by_state(found_cities[0])
                #     found_countries.append(country_name)

                print("Country:", found_countries)
                print("city:", found_cities)
            else:
                print(f"The specific word '{author_name}' was not found in the text.")

            # Medical_confirmation
            medical_keywords = ["yes", "No", "Unk"]
            general_information["medically_confirmation"] = "Yes"
            # print("Medically Confirmation:", medical_confirmation)

            # Expelled_Report
            expedited_keywords = ["true", "false"]
            expedited_report = ""
            print("Expedited report:", expedited_report)

            # First sender
            general_information["first_Sender"] = "Other"
            # print("First sender:", first_sender)

            # Nullification
            nullification_keywords = ["Nullification", "Amendment"]

            #############################################

            # Reporter
            name_parts = author_name.split()
            num_words = len(name_parts)
            first_name = ""
            middle_name = ""
            last_name = ""
            if num_words == 2:
                # If the author name has only 2 words, consider them as first and last names
                first_name = name_parts[0]
                last_name = name_parts[1]
            elif num_words == 1:
                first_name = name_parts[0]
            elif num_words >= 3:
                first_name = name_parts[0]
                middle_name = name_parts[1]
                last_name = " ".join(name_parts[2:])

            print("First name:", first_name)
            print("Middle name:", middle_name)
            print("Last name:", last_name)

            # Address



            primary_reporter = ""
            protect_confidentiality = ""
            correspondence_contact = ""

            title = ""
            first_name = ""
            middle_name = ""
            last_name = ""
            suffix = ""
            organization_name = " "
            department = ""
            qualification = ""
            health_care_professional = ""
            occupation = ""
            reporter_type = ""
            report_sent_to_regulatory_authority_by_reports = ""
            address_1 = ""
            address_2 = ""
            city_ = ""
            state_or_province = ""
            postal_code = ""
            country = ""
            phone_number = ""
            email_address = ""
            fax_number = ""
            alternate_phone = ""

            primary_reporter_corr = ""
            protect_confidentiality_corr = ""
            correspondence_contact_corr = ""

            title_correspondence = ""
            first_name_correspondence = ""
            middle_name_correspondence = ""
            last_name_correspondence = ""
            suffix_correspondence = ""
            organization_name_correspondence = " "
            department_correspondence = ""
            qualification_correspondence = ""
            health_care_professional_correspondence = ""
            occupation_correspondence = ""
            reporter_type_correspondence = ""
            report_sent_to_regulatory_authority_by_reports_correspondence = ""
            address_1_correspondence = ""
            address_2_correspondence = ""
            city_correspondence = ""
            state_or_province_correspondence = ""
            postal_code_correspondence = ""
            country_correspondence = ""
            phone_number_correspondence = ""
            email_address_correspondence = ""
            fax_number_correspondence = ""
            alternate_phone_correspondence = ""



            # Get the number of pages in the PDF



            # Initialize an empty string to store the extracted text
            anthr_text = all_text

            # Split the text by lines and search for the correspondence section
            lines = anthr_text.split('\n')

            correspondence_start = None
            correspondence_end = None

            email_pattern = r'\b[A-Za-z0-9._%+-]+\n+[^@\s]+\n+@[A-Za-z0-9.-]+\n+\.[A-Za-z]{2,}\b'
            for i, line in enumerate(lines):
                if "Correspond" in line or "CORRESPOND" in line or "CONTACT" in line or "Contact" in line:
                    correspondence_start = i
                    break
            correspondence_text = ''
            if correspondence_start is not None:
                for i in range(correspondence_start, len(lines)):
                    if re.search(email_pattern, lines[i]):
                        print("yes")
                        correspondence_end = i
                        break
                    elif '@' in lines[i]:
                        correspondence_end = i
                        break

                if correspondence_end is None:
                    correspondence_end = correspondence_start + 1

                if correspondence_end is not None:
                    correspondence_text = '\n'.join(lines[correspondence_start:correspondence_end + 1])

                    # Print the extracted correspondence section
                print("Extracted Correspondence Section:")
                print(correspondence_text)

                print("###### Reporter tab ######")

            # Correspondence and author work starts here:
            text_up_to_doi = ""
            cleaned_text = ""
            if correspondence_start is None:
                print("Correspondence Author not found")
                print("Protect Confidentiality: Yes")
                print("Primary Reporter: yes")
                primary_reporter = "yes"
                protect_confidentiality = "yes"
                correspondence_contact = "no"

                # First, middle, last names
                name_parts = author_name.split()
                num_words = len(name_parts)

                if num_words == 2:
                    # If the author name has only 2 words, consider them as first and last names
                    first_name = name_parts[0]
                    last_name = name_parts[1]
                elif num_words == 1:
                    first_name = name_parts[0]
                elif num_words >= 3:
                    first_name = name_parts[0]
                    middle_name = name_parts[1]
                    last_name = " ".join(name_parts[2:])
                print("###### Reporter tab ######")
                print("First name:", first_name)
                print("Middle name:", middle_name)
                print("Last name:", last_name)

                # suffix
                # print("Suffix:", suffix)

                # Organization name

                # print("Organization Name:", organization_name)
                extracted_text_after_author = " "
                text_after_1 = ""
                if author_name.lower() in weekly_doc.text.lower():
                    # Find the index of the specific word
                    word_index = weekly_doc.text.find(author_name)

                    # Extract text after the specific word
                    extracted_text_after_author = weekly_doc.text[word_index + len(author_name):]
                    # Initialize a variable to store the text up to the DOI line
                    text_up_to_doi = ""
                    # Iterate through the lines
                    for line in extracted_text_after_author.split("\n"):
                        if "DOI:" in line:
                            break  # Stop when the line containing "DOI:" is found
                        text_up_to_doi += line
                    index_department_of = text_up_to_doi.find('Department of')

                    if index_department_of != -1:
                        # Extract text following 'Department of'
                        department = text_up_to_doi[index_department_of:].strip().split(",")[0]

                        # Print or process the extracted department text
                    print("Department:", department)
                    # doc = nlp(extracted_text)
                    #
                    # for ent in doc.ents:
                    #     if ent.label_ == "ORG":  # Check for entities labeled as organizations
                    #         print(f"Organization: {ent.text}")

                # Qualifications
                qualifications = ["Physician", "Pharmacist", "Other health Professional", "Lawyer",
                                  "Consumer (or) Other Health Professional"]
                text_lower = text_up_to_doi.lower()
                # Check for keywords related to MBBS or Doctor
                if (
                        'mbbs' in text_lower
                        or 'doctor' in text_lower
                        or 'doctorate' in text_lower
                        or 'md' in text_lower
                        or 'phd' in text_lower
                        or 'ms' in text_lower
                        or 'bams' in text_lower
                        or 'neurologist' in text_lower
                        or 'cardiologist' in text_lower
                ):
                    qualification = qualifications[0]

                # Check for Pharmacy related degrees
                elif (
                        'b.pharm' in text_lower
                        or 'm.pharm' in text_lower
                        or 'pharm d' in text_lower
                        or 'pharmacist' in text_lower
                        or 'registered pharmacist' in text_lower
                ):
                    qualification = qualifications[1]

                else:
                    qualification = qualifications[2]
                print("qualification", qualification)

                # Health care professional
                health_care_professionals = ['Yes', 'No', 'Unk']
                if qualification == qualifications[0] or qualifications[1] or qualifications[2]:
                    health_care_professional = health_care_professionals[0]
                else:
                    health_care_professional = health_care_professionals[1]
                print("Health care professional:", health_care_professional)

                # Occupation
                occupation = ['Physician', 'Pharmacist']
                if qualification == qualifications[0]:
                    occupation_no_correspondence = occupation[0]
                elif qualification == qualifications[1]:
                    occupation = occupation[1]
                else:
                    occupation = ""

                # Reporter type
                reporter_type = ['Physician', 'Pharmacist', 'Other Health Professional']
                if qualification == qualifications[0]:
                    reporter_type = reporter_type[0]
                elif qualification == qualifications[1]:
                    reporter_type = reporter_type[1]
                else:
                    reporter_type = reporter_type[2]

                report_sent_to_regulatory_authority_by_reports = "Unk"
                print("Report sent to regulatory authority by reports:", report_sent_to_regulatory_authority_by_reports)

                # Details of primary author
                # Find text after 'Affiliations'
                affiliation_text = text_up_to_doi.split('Affiliations')[1]

                # Split the text at occurrences of '2'
                split_text = affiliation_text.split('2')

                # Get the text before the first period in the first split
                desired_text = split_text[0]
                cleaned_text = desired_text.replace('', '')
                # address
                doc = nlp(cleaned_text)

                addresses = []
                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'

                # Find email addresses in the text
                email = re.findall(email_pattern, cleaned_text)

                # Extract text that is not ORG or GPE and consider it as part of the address
                for token in doc:
                    if (
                            token.ent_type_
                            not in
                            ['ORG', 'GPE', 'PERSON']
                            and
                            token.text.lower()
                            not in
                            ['correspondence', 'text', 'contact', 'author', 'email', '*']
                            and
                            token != email
                    ):
                        if token.text.strip():
                            addresses.append(token.text)

                address_1 = ' '.join(addresses)
                print("Primary author address:", address_1)

                # city
                if found_cities:
                    city_ = found_cities[0]
                    print("primary Author city:", found_cities[0])
                else:
                    city_ = city
                    print("primary Author city:", city)

                # State

                print("Primary Author state:", state_or_province)

                # Pincode

                json_file = "postal-codes.json"
                with open(json_file, encoding='utf-8-sig') as file:
                    country_regexes = json.load(file)
                pin_codes = []
                affiliation_text = text_up_to_doi.split('Affiliations')[1]

                # Split the text at occurrences of '2'
                split_text = affiliation_text.split('2')

                # Get the text before the first period in the first split
                desired_text = split_text[0]
                for country_data in country_regexes:
                    regex_pattern = country_data["Regex"]
                    modified_pattern = r"\b" + re.sub(r'^\^|\$$', '', regex_pattern) + r"\b"

                    matches = re.findall(modified_pattern, desired_text)
                    if matches:
                        pin_codes.extend(matches)
                max_digit_count = 0
                string_with_max_digits = ''

                for string in pin_codes:
                    digit_count = sum(c.isdigit() for c in string)  # Count the number of digits in the string
                    if digit_count > max_digit_count:
                        max_digit_count = digit_count
                        postal_code = string
                print("Primary Author Pincode:", postal_code)

                # Country
                country = found_countries
                print("Primary Author Country", found_countries)

                # Phone number

                print("Primary Author phone number:", phone_number)

                # Email pattern
                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'
                # Find email addresses in the text
                email_address = re.findall(email_pattern, text_up_to_doi)
                if email_address:
                    local_part = email_address[0].split('@')
                    # Check if the author's name is present in the local part
                    author = author_name  # Replace with the author's name you're checking for
                    if author in local_part:
                        email_address = email_address
                print("primary Author email:", email_address)

                # Fax number
                lines = desired_text.split('\n')

                # Variable to store the extracted phone numbers

                # Find the line containing 'Fax' or 'Tel' and extract text after that
                for line in lines:
                    if 'Fax' in line or 'Tel' in line or '+' in line:
                        # Extract the text after 'Fax' or 'Tel'
                        # extracted_text = line.split('Fax:')[-1].strip() if 'Fax' in line else line.split('Tel:')[-1].strip()
                        extracted_text = line

                        # Extract numbers with the '+' character
                        numbers_with_plus = re.findall(r'\+\d[\d -]+', extracted_text)
                        numbers_with_plus_in_brackets = re.findall(r'\(\+\d+\)-\d+', line)
                        numbers_with_plus_in_brackets_and_space = re.findall(r'\(\+\d+\) \d+', line)
                        if numbers_with_plus:
                            fax_number = numbers_with_plus
                        elif numbers_with_plus_in_brackets:
                            fax_number = numbers_with_plus_in_brackets
                        elif numbers_with_plus_in_brackets_and_space:
                            fax_number = numbers_with_plus_in_brackets_and_space

                print("Primary Author Fax Number", fax_number)

                # Alternate number

                print("Primary Author Alternate number:", alternate_phone)

            elif first_name in correspondence_text or last_name in correspondence_text:
                print("Protect Confidentiality: Yes")
                print("Primary Reporter: yes")
                print("Correspondence contact: Yes")
                print("primary author and Correspondence author are same.")
                primary_reporter = "yes"
                protect_confidentiality = "yes"
                correspondence_contact = "yes"
                # Details of correspondence and primary author
                # First, middle, last names
                name_parts = author_name.split()
                num_words = len(name_parts)

                if num_words == 2:
                    # If the author name has only 2 words, consider them as first and last names
                    first_name = name_parts[0]
                    last_name = name_parts[1]
                elif num_words == 1:
                    first_name = name_parts[0]
                elif num_words >= 3:
                    first_name = name_parts[0]
                    middle_name = name_parts[1]
                    last_name = " ".join(name_parts[2:])
                print("###### Reporter tab ######")
                print("First name:", first_name)
                print("Middle name:", middle_name)
                print("Last name:", last_name)

                # suffix

                print("Suffix:", suffix)

                # Organization name

                print("Organization Name:", organization_name)
                extracted_text = " "
                department_text = ""
                if author_name.lower() in weekly_doc.text.lower():
                    # Find the index of the specific word
                    word_index = weekly_doc.text.find(author_name)

                    # Extract text after the specific word
                    extracted_text_after_author = weekly_doc.text[word_index + len(author_name):]
                    # Initialize a variable to store the text up to the DOI line
                    text_up_to_doi = ""
                    # Iterate through the lines
                    for line in extracted_text_after_author.split("\n"):
                        if "DOI:" in line:
                            break  # Stop when the line containing "DOI:" is found
                        text_up_to_doi += line
                    index_department_of = text_up_to_doi.find('Department of')
                    if index_department_of != -1:
                        # Extract text following 'Department of'
                        department = text_up_to_doi[index_department_of:].strip().split(",")[0]

                        # Print or process the extracted department text
                    print("Department:", department)
                else:
                    department = department_text
                    print("Department:", department)

                # Qualifications
                qualifications = ["Physician", "Pharmacist", "Other Health Professional", "Lawyer",
                                  "Consumer (or) Other Health Professional"]
                text_lower = correspondence_text.lower()
                print("text_lower", text_lower)

                # Check for keywords related to MBBS or Doctor
                if (
                        'mbbs' in text_lower
                        or 'doctor' in text_lower
                        or 'doctorate' in text_lower
                        or 'md' in text_lower
                        or 'm.d' in text_lower
                        or 'ph.d' in text_lower
                        or 'phd' in text_lower
                        or 'ms' in text_lower
                        or 'bams' in text_lower
                        or 'neurologist' in text_lower
                        or 'cardiologist' in text_lower
                ):
                    qualification = qualifications[0]

                # Check for Pharmacy related degrees
                elif (
                        'b.pharm' in text_lower
                        or 'm.pharm' in text_lower
                        or 'pharm d' in text_lower
                        or 'pharmacist' in text_lower
                        or 'registered pharmacist' in text_lower
                ):
                    qualification = qualifications[1]

                else:
                    qualification = qualifications[2]
                print("Qualification:", qualification)

                # Health care professional
                health_care_professionals = ['Yes', 'No', 'Unk']

                if qualification == qualifications[0] or qualifications[1] or qualifications[2]:
                    health_care_professional = health_care_professionals[0]
                else:
                    health_care_professional = health_care_professionals[1]
                print("Health care professional:", health_care_professional)

                # Occupation
                occupation = ['Physician', 'Pharmacist']
                if qualification == qualifications[0]:
                    occupation = occupation[0]
                elif qualification == qualifications[1]:
                    occupation = occupation[1]
                else:
                    occupation = ""

                # Reporter type
                reporter_type_keywords = ['Physician', 'Pharmacist', 'Other Health Professional']
                if qualification == qualifications[0]:
                    reporter_type = reporter_type_keywords[0]
                elif qualification == qualifications[1]:
                    reporter_type = reporter_type_keywords[1]
                else:
                    reporter_type = reporter_type_keywords[2]

                report_sent_to_regulatory_authority_by_reports = "Unk"
                print("Report sent to regulatory authority by reports:", report_sent_to_regulatory_authority_by_reports)

                # City
                corr_city = []
                corr_city_from_affiliation = []
                affiliations = correspondence_text.split("\n")
                # Loop through affiliations and search for country names and cities
                for affiliation in affiliations:
                    country_doc = nlp(affiliation)
                    if found_cities[0] in affiliation:
                        city_ = found_cities[0]

                    else:
                        for token in country_doc:
                            if token.ent_type_ == "GPE" and token.text:
                                if not is_part_of_city:
                                    is_part_of_city = True
                                    city = token.text
                                else:
                                    city += " " + token.text
                            else:
                                if is_part_of_city:
                                    corr_city.append(city)
                                    is_part_of_city = False
                                    city = ""
                print("Correspondence Author city:", city_)
                # If the city string isn't finished at the end
                if is_part_of_city and not corr_city_from_affiliation:
                    corr_city.append(city)
                    city_ = corr_city[0]
                    print("Correspondence Author city:", corr_city[0])

                # address
                doc = nlp(correspondence_text)

                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'

                # Find email addresses in the text
                email = re.findall(email_pattern, correspondence_text)

                # Extract text that is not ORG or GPE and consider it as part of the address
                addresses = [token.text for token in doc if (
                        token.ent_type_ not in {'ORG', 'GPE', 'PERSON'}
                        and token.text.lower() not in {'correspondence', 'text', 'contact', 'author', 'email', '*'}
                        and token.text not in email
                        and token.text.strip()
                )]

                # Join the address parts into a string
                address_1 = ' '.join(addresses)

                if not addresses:
                    # Find email addresses in the text
                    email = re.findall(email_pattern, cleaned_text)

                    # Extract text that is not ORG or GPE and consider it as part of the address
                    addresses = [token.text for token in doc if (
                            token.ent_type_ not in {'ORG', 'GPE', 'PERSON'}
                            and token.text.lower() not in {'correspondence', 'text', 'contact', 'author', 'email', '*'}
                            and token.text not in email
                            and token.text.strip()
                    )]

                    # Join the address parts into a string
                    address_1 = ' '.join(addresses)
                else:
                    address_1 = ' '.join(addresses)
                    print("Address:", addresses)

                # Pincode
                def extract_pin_code(text, country_regexes):
                    pin_codes = []

                    for country_data in country_regexes:
                        regex_pattern = country_data["Regex"]
                        modified_pattern = r"\b" + re.sub(r'^\^|\$$', '', regex_pattern) + r"\b"
                        matches = re.findall(modified_pattern, text)

                        if matches:
                            pin_codes.extend(matches)

                    max_digit_count = 0
                    pin_code = ''

                    for string in pin_codes:
                        digit_count = sum(c.isdigit() for c in string)
                        if digit_count > max_digit_count:
                            max_digit_count = digit_count
                            pin_code = string

                    return pin_code

                correspondence_doc = nlp(correspondence_text)
                json_file = "postal-codes.json"

                with open(json_file, encoding='utf-8-sig') as file:
                    country_regexes = json.load(file)

                postal_code = extract_pin_code(correspondence_text, country_regexes)

                if not postal_code:
                    if author_name.lower() in weekly_doc.text.lower():
                        # Find the index of the specific word
                        word_index = weekly_doc.text.find(author_name)

                        # Extract text after the specific word
                        extracted_text_after_author = weekly_doc.text[word_index + len(author_name):]
                        # Initialize a variable to store the text up to the DOI line
                        text_up_to_doi = ""
                        # Iterate through the lines
                        for line in extracted_text_after_author.split("\n"):
                            if "DOI:" in line:
                                break  # Stop when the line containing "DOI:" is found
                            text_up_to_doi += line

                    affiliation_text = text_up_to_doi.split('Affiliations')[1]
                    split_text = affiliation_text.split('2')
                    desired_text = split_text[0]

                    postal_code = extract_pin_code(desired_text, country_regexes)

                print("Pincode:", postal_code)

                # Country
                if found_countries:
                    country = found_countries
                    print("Country:", found_countries)
                else:
                    affiliations = correspondence_text.split("\n")
                    corr_country = ""
                    country_found = False
                    for affiliation in affiliations:
                        deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan', 'MACAU',
                                             'Republic Of Ireland']
                        for i in deleted_countries:
                            if i in affiliation:
                                if not country_found:
                                    corr_country = i
                                    country_found = True

                        for country in pycountry.countries:
                            if country.name in affiliation:
                                corr_country = country.name
                                break
                    print("Country:", corr_country)
                    country = corr_country

                # Phone number

                print("phone number:", phone_number)

                # Define a regular expression pattern to capture email addresses
                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'
                # Find email addresses in the text
                email = re.findall(email_pattern, correspondence_text)

                if email:
                    email_address = email[0]
                    print("Email Address:", email[0])
                else:
                    email_address = re.findall(email_pattern, all_text)
                    print("Email Address:", email_address)

                # Fax number
                lines = correspondence_text.split('\n')

                # Variable to store the extracted phone numbers

                # Find the line containing 'Fax' or 'Tel' and extract text after that
                for line in lines:
                    if 'Fax' in line or 'Tel' in line or '+' in line:
                        # Extract the text after 'Fax' or 'Tel'
                        # extracted_text = line.split('Fax:')[-1].strip() if 'Fax' in line else line.split('Tel:')[-1].strip()
                        extracted_text = line

                        # Extract numbers with the '+' character
                        numbers_with_plus = re.findall(r'\+\d[\d -]+', extracted_text)
                        numbers_with_plus_in_brackets = re.findall(r'\(\+\d+\)-\d+', line)
                        numbers_with_plus_in_brackets_and_space = re.findall(r'\(\+\d+\) \d+', line)
                        if numbers_with_plus:
                            fax_number = numbers_with_plus
                        elif numbers_with_plus_in_brackets:
                            fax_number = numbers_with_plus_in_brackets
                        elif numbers_with_plus_in_brackets_and_space:
                            fax_number = numbers_with_plus_in_brackets_and_space
                print("Fax Number:", fax_number)

                # Alternate number

                print("Alternate number:", alternate_phone)

                title_correspondence = title
                first_name_correspondence = first_name
                middle_name_correspondence = middle_name
                last_name_correspondence = last_name
                suffix_correspondence = suffix
                organization_name_correspondence = organization_name
                department_correspondence = department
                qualification_correspondence = qualification
                health_care_professional_correspondence = health_care_professional
                occupation_correspondence = occupation_correspondence
                reporter_type_correspondence = reporter_type
                report_sent_to_regulatory_authority_by_reports_correspondence = report_sent_to_regulatory_authority_by_reports
                address_1_correspondence = address_1
                address_2_correspondence = address_2
                city_correspondence = city_
                state_or_province_correspondence = state_or_province
                postal_code_correspondence = postal_code
                country_correspondence = country
                phone_number_correspondence = phone_number
                email_address_correspondence = email_address
                fax_number_correspondence = fax_number
                alternate_phone_correspondence = alternate_phone
            else:
                print("Primary Author is different to correspondence author")
                print("Protect Confidentiality: Yes")
                print("Primary Reporter: yes")
                primary_reporter = "yes"
                protect_confidentiality = "yes"
                correspondence_contact = "no"

                primary_reporter_corr = "no"
                protect_confidentiality_corr = "yes"
                correspondence_contact_corr = "yes"
                # Details of primary author
                name_parts = author_name.split()
                num_words = len(name_parts)
                # first_name = ""
                # middle_name = ""
                # last_name = ""
                if num_words == 2:
                    # If the author name has only 2 words, consider them as first and last names
                    first_name = name_parts[0]
                    last_name = name_parts[1]
                elif num_words == 1:
                    first_name = name_parts[0]
                elif num_words >= 3:
                    first_name = name_parts[0]
                    middle_name = name_parts[1]
                    last_name = " ".join(name_parts[2:])
                print("###### Reporter tab ######")
                print("First name:", first_name)
                print("Middle name:", middle_name)
                print("Last name:", last_name)

                # suffix

                print("Suffix:", suffix)

                # Organization name
                # organization_name = " "
                print("Organization Name:", organization_name)
                extracted_text_after_author = " "
                department_text = ""
                if author_name.lower() in weekly_doc.text.lower():
                    # Find the index of the specific word
                    word_index = weekly_doc.text.find(author_name)

                    # Extract text after the specific word
                    extracted_text_after_author = weekly_doc.text[word_index + len(author_name):]
                    # Initialize a variable to store the text up to the DOI line
                    text_up_to_doi = ""
                    # Iterate through the lines
                    for line in extracted_text_after_author.split("\n"):
                        if "DOI:" in line:
                            break  # Stop when the line containing "DOI:" is found
                        text_up_to_doi += line
                    index_department_of = text_up_to_doi.find('Department of')

                    if index_department_of != -1:
                        # Extract text following 'Department of'
                        department = text_up_to_doi[index_department_of:].strip().split(",")[0]

                        # Print or process the extracted department text
                    print("Extracted Department Text:", department)

                # Qualifications
                qualifications = ["Physician", "Pharmacist", "Other health Professional", "Lawyer",
                                  "Consumer (or) Other Health Professional"]
                text_lower = text_up_to_doi.lower()
                # Check for keywords related to MBBS or Doctor
                if (
                        'mbbs' in text_lower
                        or 'doctor' in text_lower
                        or 'doctorate' in text_lower
                        or 'md' in text_lower
                        or 'phd' in text_lower
                        or 'ms' in text_lower
                        or 'bams' in text_lower
                        or 'neurologist' in text_lower
                        or 'cardiologist' in text_lower
                ):
                    qualification = qualifications[0]

                # Check for Pharmacy related degrees
                elif (
                        'b.pharm' in text_lower
                        or 'm.pharm' in text_lower
                        or 'pharm d' in text_lower
                        or 'pharmacist' in text_lower
                        or 'registered pharmacist' in text_lower
                ):
                    qualification = qualifications[1]

                else:
                    qualification = qualifications[2]
                print("Qualification:", qualification)

                # Health care professional
                health_care_professionals = ['Yes', 'No']

                if qualification == qualifications[0] or qualifications[1] or qualifications[2]:
                    health_care_professional = health_care_professionals[0]
                else:
                    health_care_professional = health_care_professionals[1]
                print("Health care professional:", health_care_professional)

                # Occupation
                occupation = ['Physician', 'Pharmacist']
                if qualification == qualifications[0]:
                    occupation = occupation[0]
                elif qualification == qualifications[1]:
                    occupation = occupation[1]
                else:
                    occupation = ""

                # Reporter type
                reporter_type_keywords = ['Physician', 'Pharmacist', 'Other Health Professional']
                if qualification == qualifications[0]:
                    reporter_type = reporter_type_keywords[0]
                elif qualification == qualifications[1]:
                    reporter_type = reporter_type_keywords[1]
                else:
                    reporter_type = reporter_type_keywords[2]

                report_sent_to_regulatory_authority_by_reports = "Unk"
                print("Report sent to regulatory authority by reports:", report_sent_to_regulatory_authority_by_reports)

                # Find text after 'Affiliations'
                affiliation_text = text_up_to_doi.split('Affiliations')[1]

                # Split the text at occurrences of '2'
                split_text = affiliation_text.split('2')

                # Get the text before the first period in the first split
                desired_text = split_text[0]
                cleaned_text = desired_text.replace('', '')
                # Address
                doc = nlp(cleaned_text)

                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'

                # Find email addresses in the text
                email = re.findall(email_pattern, cleaned_text)

                # Extract text that is not ORG or GPE and consider it as part of the address
                addresses = [token.text for token in doc if (
                        token.ent_type_ not in {'ORG', 'GPE', 'PERSON'}
                        and token.text.lower() not in {'correspondence', 'text', 'contact', 'author', 'email', '*'}
                        and token.text not in email
                        and token.text.strip()
                )]

                # Join the address parts into a string
                address_1 = ' '.join(addresses)
                print("address:", address_1)

                # city
                city_ = found_cities[0]
                print("primary Author city:", found_cities[0])

                # State

                print("Primary Author state:", state_or_province)

                # Pincode

                json_file = "postal-codes.json"
                with open(json_file, encoding='utf-8-sig') as file:
                    country_regexes = json.load(file)
                pin_codes = []
                affiliation_text = text_up_to_doi.split('Affiliations')[1]

                # Split the text at occurrences of '2'
                split_text = affiliation_text.split('2')

                # Get the text before the first period in the first split
                desired_text = split_text[0]
                for country_data in country_regexes:
                    regex_pattern = country_data["Regex"]
                    modified_pattern = r"\b" + re.sub(r'^\^|\$$', '', regex_pattern) + r"\b"

                    matches = re.findall(modified_pattern, desired_text)
                    if matches:
                        pin_codes.extend(matches)
                max_digit_count = 0
                string_with_max_digits = ''

                for string in pin_codes:
                    digit_count = sum(c.isdigit() for c in string)  # Count the number of digits in the string
                    if digit_count > max_digit_count:
                        max_digit_count = digit_count
                        postal_code = string
                print("Primary Author Pincode:", postal_code)

                # Country
                country = found_countries
                print("Primary Author Country", found_countries)

                # Phone number

                print("Primary Author phone number:", phone_number)

                # Email pattern

                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'
                # Find email addresses in the text
                email_address = re.findall(email_pattern, text_up_to_doi)
                if email_address:
                    local_part = email_address[0].split('@')
                    # Check if the author's name is present in the local part
                    author = author_name  # Replace with the author's name you're checking for
                    if author in local_part:
                        email_address = email_address
                print("primary Author email:", email_address)

                # Fax number
                lines = desired_text.split('\n')

                # Variable to store the extracted phone numbers

                # Find the line containing 'Fax' or 'Tel' and extract text after that
                for line in lines:
                    if 'Fax' in line or 'Tel' in line or '+' in line:
                        # Extract the text after 'Fax' or 'Tel'
                        # extracted_text = line.split('Fax:')[-1].strip() if 'Fax' in line else line.split('Tel:')[-1].strip()
                        extracted_text = line

                        # Extract numbers with the '+' character
                        numbers_with_plus = re.findall(r'\+\d[\d -]+', extracted_text)
                        numbers_with_plus_in_brackets = re.findall(r'\(\+\d+\)-\d+', line)
                        numbers_with_plus_in_brackets_and_space = re.findall(r'\(\+\d+\) \d+', line)
                        if numbers_with_plus:
                            fax_number = numbers_with_plus
                        elif numbers_with_plus_in_brackets:
                            fax_number = numbers_with_plus_in_brackets
                        elif numbers_with_plus_in_brackets_and_space:
                            fax_number = numbers_with_plus_in_brackets_and_space

                print("Primary Author Fax Number", fax_number)

                # Alternate number

                print("Primary Author Alternate number:", alternate_phone)

                ##### Details of Correspondence author #####
                print("Correspondence author starts")
                print("Protect Confidentiality: Yes")
                print("Correspondence contact: yes")
                matched_author = ""
                authors = []
                # First name
                for i, line in enumerate(text_lines):
                    if "Author" in line or "Authors" in line:
                        if i + 1 < len(text_lines):
                            # Split the line by commas and extract all the names
                            author_names = text_lines[i + 1].split(',')

                            # Clean up the names (remove leading/trailing spaces)
                            author_names = [name.strip() for name in author_names]

                            for name in author_names:
                                name = name.strip()
                                name_without_numbers = ''.join(filter(lambda x: not x.isdigit(), name))
                                authors.append(name_without_numbers.strip())

                        for name in authors:
                            if name in correspondence_text:
                                matched_author = name
                                break
                print("finally authors", authors)
                print("Matched Author Name in Corresponding Text:", matched_author)
                name_parts_corr = matched_author.split()
                num_words = len(name_parts_corr)
                if num_words == 2:
                    # If the author name has only 2 words, consider them as first and last names
                    first_name_correspondence = name_parts_corr[0]
                    last_name_correspondence = name_parts_corr[1]
                elif num_words == 1:
                    first_name_correspondence = name_parts_corr[0]
                elif num_words >= 3:
                    first_name_correspondence = name_parts_corr[0]
                    middle_name_correspondence = name_parts_corr[1]
                    last_name_correspondence = " ".join(name_parts_corr[2:])
                ###############################################################################################################
                print("First name:", first_name_correspondence)
                print("Middle name:", middle_name_correspondence)
                print("Last name:", last_name_correspondence)
                print("Suffix:", suffix)
                print("Organization Name:", organization_name_correspondence)
                # Department
                extracted_text = " "
                department_text = ""
                index_department_of = correspondence_text.find('Department of')

                if index_department_of != -1:
                    # Extract text following 'Department of'
                    department_correspondence = correspondence_text[index_department_of:].strip().split(",")[0]

                    # Print or process the extracted department text
                print("Extracted Department Text:", department_correspondence)

                # Qualifications
                qualifications = ["Physician", "Pharmacist", "Other Health Professional", "Lawyer",
                                  "Consumer (or) Other Health Professional"]
                text_lower = correspondence_text.lower()

                # Check for keywords related to MBBS or Doctor
                if (
                        'mbbs' in text_lower
                        or 'doctor' in text_lower
                        or 'doctorate' in text_lower
                        or 'md' in text_lower
                        or 'phd' in text_lower
                        or 'ms' in text_lower
                        or 'bams' in text_lower
                        or 'neurologist' in text_lower
                        or 'cardiologist' in text_lower
                ):
                    qualification_correspondence = qualifications[0]

                # Check for Pharmacy related degrees
                elif (
                        'b.pharm' in text_lower
                        or 'm.pharm' in text_lower
                        or 'pharm d' in text_lower
                        or 'pharmacist' in text_lower
                        or 'registered pharmacist' in text_lower
                ):
                    qualification_correspondence = qualifications[1]

                else:
                    qualification_correspondence = qualifications[2]
                print("Qualification:", qualification_correspondence)

                # Health care professional
                health_care_professionals = ['yes', 'No']

                if qualification_correspondence == qualifications[0] or qualifications[1] or qualifications[2]:
                    health_care_professional_correspondence = health_care_professionals[0]
                else:
                    health_care_professional_correspondence = health_care_professionals[1]
                print("Health care professional:", health_care_professional_correspondence)

                # Occupation
                occupation_keywords = ['Physician', 'Pharmacist']
                if qualification_correspondence == qualifications[0]:
                    occupation_correspondence = occupation_keywords[0]
                elif qualification_correspondence == qualifications[1]:
                    occupation_correspondence = occupation_keywords[1]
                else:
                    occupation_correspondence = ""
                print("occupation", occupation_correspondence)
                # Reporter type
                reporter_type_keywords = ['Physician', 'Pharmacist', 'Other Health Professional']

                if qualification_correspondence == qualifications[0]:
                    reporter_type_correspondence = reporter_type_keywords[0]
                elif qualification_correspondence == qualifications[1]:
                    reporter_type_correspondence = reporter_type_keywords[1]
                else:
                    reporter_type_correspondence = reporter_type_keywords[2]

                print("Report sent to regulatory authority by reports:",
                      report_sent_to_regulatory_authority_by_reports_correspondence)

                # Address
                doc = nlp(correspondence_text)

                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'

                # Find email addresses in the text
                email = re.findall(email_pattern, correspondence_text)

                # Extract text that is not ORG or GPE and consider it as part of the address
                addresses = [token.text for token in doc if (
                        token.ent_type_ not in {'ORG', 'GPE', 'PERSON'}
                        and token.text.lower() not in {'correspondence', 'text', 'contact', 'author', 'email', '*'}
                        and token.text not in email
                        and token.text.strip()
                )]

                # Join the address parts into a string
                address_1_correspondence = ' '.join(addresses)
                print("Correspondence address:", address_1_correspondence)
                #  city
                corr_city = ""

                affiliations = correspondence_text.split("\n")
                # Loop through affiliations and search for country names and cities
                for affiliation in affiliations:
                    country_doc = nlp(affiliation)
                    if found_cities[0] in affiliation:
                        city_correspondence = found_cities[0]

                    else:
                        for token in country_doc:
                            if token.ent_type_ == "GPE" and token.text:
                                if not is_part_of_city:
                                    is_part_of_city = True
                                    city = token.text
                                else:
                                    city += " " + token.text
                            else:
                                if is_part_of_city:
                                    corr_city = city
                                    is_part_of_city = False
                                    city = ""
                print("Correspondence Author city:", city_correspondence)
                # If the city string isn't finished at the end
                if is_part_of_city and not city_correspondence:
                    city_correspondence = city
                    print("Correspondence Author city:", city_correspondence)
                # correspondence_doc = nlp(correspondence_text)
                # for entity in correspondence_doc:
                #     if entity.ent_type_ == "GPE":
                #         city = entity.text
                #         corresponding_author_city.append(city)
                #         break
                # print("Correspondence Author city:", corresponding_author_city)
                # State

                print("Correspondence Author state:", state_or_province_correspondence)
                # Pincode
                pin_code = " "
                json_file = "postal-codes.json"
                # Define a regular expression pattern to capture email addresses
                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'

                # Find email addresses in the text
                email = re.findall(email_pattern, correspondence_text)

                with open(json_file, encoding='utf-8-sig') as file:
                    country_regexes = json.load(file)
                pin_codes = []
                for country_data in country_regexes:
                    regex_pattern = country_data["Regex"]
                    modified_pattern = r"\b" + re.sub(r'^\^|\$$', '', regex_pattern) + r"\b"
                    matches = re.findall(modified_pattern + r'(?!\S+@\S+)', correspondence_text)
                    if matches:
                        # Adjust the regular expression to focus only on the pin code pattern
                        matches = re.findall(modified_pattern, correspondence_text)
                        if matches:
                            # Exclude digits from within identified email addresses
                            for mail in email:
                                correspondence_text = correspondence_text.replace(mail,
                                                                                  '')  # Remove the email from the text

                            # Find pin codes in the modified text
                            pin_codes.extend(re.findall(modified_pattern, correspondence_text))
                        pin_codes.extend(matches)
                max_digit_count = 0
                string_with_max_digits = ''

                for string in pin_codes:
                    digit_count = sum(c.isdigit() for c in string)  # Count the number of digits in the string
                    if digit_count > max_digit_count:
                        max_digit_count = digit_count
                        postal_code_correspondence = string

                print("Correspondence Author pincode:", postal_code_correspondence)
                # for token in correspondence_doc:
                #     if len(token.text) == 6 and token.text.isdigit():
                #         pin_code = token.text
                # print("Pincode:", pin_code)

                # Country
                affiliations = correspondence_text.split("\n")
                corr_country = ""
                country_from_corr = ""
                country_found = False
                for affiliation in affiliations:
                    deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan', 'MACAU',
                                         'Republic Of Ireland']
                    for i in deleted_countries:
                        if i in affiliation:
                            if not country_found:
                                corr_country = i
                                country_found = True

                    for country in pycountry.countries:
                        if country.name in affiliation:
                            country_from_corr = country.name
                            break
                if corr_country:
                    country_correspondence = corr_country
                else:
                    country_correspondence = country_from_corr
                print("Correspondence Author Country:", country_correspondence)

                # Phone number

                print("Correspondence Author phone number:", phone_number_correspondence)

                # Define a regular expression pattern to capture email addresses
                # From pincode part
                email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'
                # Find email addresses in the text
                email = re.findall(email_pattern, correspondence_text)

                email_address_correspondence = email
                if email:
                    print("Correspondence Author Email Address:", email_address_correspondence)
                elif not email:
                    email_address = re.findall(email_pattern, all_text)
                    email_address_correspondence = email_address[0]
                    print("Correspondence Author Email address:", email_address_correspondence)
                else:
                    print("Correspondence Author Email address:", email_address_correspondence)

                # Fax-number

                lines = correspondence_text.split('\n')

                # Variable to store the extracted phone numbers
                # fax_numbers = []

                # Find the line containing 'Fax' or 'Tel' and extract text after that
                for line in lines:
                    if 'Fax' in line or 'Tel' in line or '+' in line:
                        # Extract the text after 'Fax' or 'Tel'
                        # extracted_text = line.split('Fax:')[-1].strip() if 'Fax' in line else line.split('Tel:')[-1].strip()
                        extracted_text = line

                        # Extract numbers with the '+' character
                        numbers_with_plus = re.findall(r'\+\d[\d -]+', extracted_text)
                        numbers_with_plus_in_brackets = re.findall(r'\(\+\d+\)-\d+', line)
                        numbers_with_plus_in_brackets_and_space = re.findall(r'\(\+\d+\) \d+', line)
                        if numbers_with_plus:
                            fax_number_correspondence = numbers_with_plus
                        elif numbers_with_plus_in_brackets:
                            fax_number_correspondence = numbers_with_plus_in_brackets
                        elif numbers_with_plus_in_brackets_and_space:
                            fax_number_correspondence = numbers_with_plus_in_brackets_and_space
                print("Correspondence Author Fax Number:", fax_number_correspondence)

                # Alternate number
                alternate_number = ""
                print("Correspondence Author Alternate number:", alternate_number)


            reporter = {
                "reporter_information": [
                    {
                        "primary_reporter": primary_reporter,
                        "protect_confidentiality": protect_confidentiality,
                        "correspondence_contact": correspondence_contact,
                        "title": title,
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "suffix": suffix,
                        "organization_name": organization_name,
                        "department": department,
                        "qualification": qualification,
                        "health_care_professional": health_care_professional,
                        "occupation": occupation,
                        "reporter_type": reporter_type,
                        "report_sent_to_regulatory_authority_by_reports": report_sent_to_regulatory_authority_by_reports,
                        "address_1": address_1,
                        "address_2": address_2,
                        "city": city_,
                        "state": state_or_province,
                        "postal_code": postal_code,
                        "country": country,
                        "phone_number": phone_number,
                        "email_address": email_address,
                        "fax_number": fax_number,
                        "alternate_phone": alternate_phone
                    },
                    {
                        "primary_reporter": primary_reporter_corr,
                        "protect_confidentiality": protect_confidentiality_corr,
                        "correspondence_contact": correspondence_contact_corr,
                        "title": title_correspondence,
                        "first_name": first_name_correspondence,
                        "middle_name": middle_name_correspondence,
                        "last_name": last_name_correspondence,
                        "suffix": suffix_correspondence,
                        "organization_name": organization_name_correspondence,
                        "department": department_correspondence,
                        "qualification": qualification_correspondence,
                        "health_care_professional": health_care_professional_correspondence,
                        "occupation": occupation_correspondence,
                        "reporter_type": reporter_type_correspondence,
                        "report_sent_to_regulatory_authority_by_reports": report_sent_to_regulatory_authority_by_reports_correspondence,
                        "address_1": address_1_correspondence,
                        "address_2": address_2_correspondence,
                        "city": city_correspondence,
                        "state": state_or_province_correspondence,
                        "postal_code": postal_code_correspondence,
                        "country": country_correspondence,
                        "phone_number": phone_number_correspondence,
                        "email_address": email_address_correspondence,
                        "fax_number": fax_number_correspondence,
                        "alternate_phone": alternate_phone_correspondence
                    }
                ],
                "literature_information": {
                    "literature_reference": literature_reference,
                    "author": author,
                    "year": year,
                    "digital_object_identifier": digital_object_identifier,
                    "literature_title": title_of_page,
                    "vol": vol,
                    "journal": journal,
                    "pages": pages
                }
            }

        else:
            raise HTTPException(status_code=13, detail="Cannot extract content because of title not found")
        return general_information, reporter
    except Exception as e:
        print('Error! Code: {c}, Message, {m}'.format(c=type(e).__name__, m=str(e)))




# general_extraction, reporter_extraction = get_general_reporter(
#             source_text=all_text,
#             weekly_text_1=weekly_text,
#             en_core=nlp,
#             meta_data=meta
#         )
# print(general_extraction, reporter_extraction)