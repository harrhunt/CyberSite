import json
import re
from csv import reader


def keywords_to_json():
    search = re.compile(r"\([A-z0-9]+\)")
    data = {}
    with open(".data/database/keywords_edited.csv", "r") as file:
        csv_reader = reader(file)
        for row in csv_reader:
            keyword = row[0]
            acronym = search.search(keyword)
            if acronym:
                keyword = keyword[:(acronym.start() - 1)]
                dat = {"acronym": acronym.group()[1:-1]}
            else:
                dat = {"acronym": ""}
            dat["sources"] = [source for source in row[1:] if source != ""]
            if keyword in data:
                print("Duplicate Keyword ", keyword)
            data[keyword] = dat
    with open(".data/database/keywords_edited.json", "w") as file:
        json.dump(data, file)


if __name__ == '__main__':
    keywords_to_json()
