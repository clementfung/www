import xml.etree.ElementTree as ET
import pandas as pd
from django.utils.encoding import smart_str

import pdb

keys_i_care_about = ['title', 'venue', 'year', 'ee']
year_list = list()
starting_year = 2017


def parse_faculty_obj(pub_dict, faculty_file):

    blacklist_file = open("blacklist")
    blacklist = [line.strip() for line in blacklist_file]

    tree = ET.parse(faculty_file)
    root = tree.getroot()
    total_parsed = 0

    # This whole part is very specific to how the DBLP API looks.
    # The XML element "hits" is the one with everything
    for hit in root.find('hits'):

        # Get a unique id for each pub
        pub_id = hit.get('id')
        hit_info = hit[0]

        # Are all needed tags there?
        has_all = True

        # A flat dictionary for one publication
        pub_obj = dict()

        # if hit_info.find('year') is None:
        #     continue

        # # Top level dictionary indexed by year.
        year = hit_info.find('year').text

        # Skip anything outside of the desired year range
        if year not in year_list:
            continue

        # Skip two odd Alan Wagner copies
        if hit_info.find("venue").text == "ICSR" or hit_info.find("venue").text == "AI Magazine":
            print "Skipping " + pub_id + " since it is blacklisted"
            continue

        # Skip anything in "proceedings of..."
        if hit_info.find("type").text == "Editorship":
            continue

        # Init year dict if not present
        # if year not in pub_dict:
        #     pub_dict[year] = dict()

        # Skip repearted publication ID
        if pub_id in pub_dict:
            # print pub_id + " is already present."
            continue

        # Get authors
        if hit_info.find('authors') is None:
            has_all = False

        author_elems = hit_info.find('authors')
        author_list = list()
        for author in author_elems:
            author_list.append(author.text)

        pub_obj['authors'] = author_list

        # Get all other keys
        for key in keys_i_care_about:

            if hit_info.find(key) is None:
                has_all = False
            else:
                pub_obj[key] = hit_info.find(key).text

        # Add to the faculty_obj if all keys are there
        if has_all:

            pub_dict[pub_id] = pub_obj
            total_parsed += 1

    return pub_dict, total_parsed


def pub_dict_to_html(pub_dict):

    # convert to pandas for easy sorting
    df = pd.DataFrame.from_dict(pub_dict, orient="index")

    df = df.sort_values(['year', 'venue'], ascending=[False, True])

    file_obj = open("pub_list.html", 'w')

    current_year = 0

    for index, row in df.iterrows():

        # Write a new year header if the year changes
        year = row['year']
        if not year == current_year:
            if not current_year == 0:
                file_obj.write("</ul>\n")

            current_year = year
            file_obj.write("<h3>" + year + "</h3>\n")
            file_obj.write("<ul>\n")

        file_obj.write("<li>\n")
        file_obj.write(
            "<strong>" + smart_str(row['title']) + "</strong>\n")

        author_string = ", ".join(row['authors'])

        file_obj.write(smart_str(author_string) + ".\n")

        file_obj.write(row['venue'] + "\n")
        file_obj.write(year + ".\n")
        file_obj.write(
            "[<a href=\"" + smart_str(row['ee']) + "\">link</a>]\n")
        file_obj.write("</li>\n")

    file_obj.write("</ul>\n")


if __name__ == "__main__":

    # Take from the current year, go back 10 years
    for i in range(15):
        year_list.append(str(starting_year - i))

    faculty_files = ["andy.xml", "ivan.xml", "bill.xml",
                     'alan.xml', 'norm.xml', 'mike.xml']

    # dictionary by year
    pub_dict = dict()
    total_count = 0

    for file in faculty_files:
        faculty_dict, count = parse_faculty_obj(pub_dict, file)
        print "Parsed " + str(count) + " publications for " + file
        total_count += count

    print "Parsed " + str(total_count) + " in total."

    pub_dict_to_html(pub_dict)

    print "Done writing to HTML."
