import csv
from decimal import *
from pprint import pprint


def main():
    people = {}

    with open("Transactions2014.csv", "r") as f:
        data_2014 = [tuple(row) for row in csv.reader(f, delimiter=',')][1:]

    for row in data_2014:
        r_date = row[0]
        r_from = row[1]
        r_to = row[2]
        r_narrative = row[3]
        r_amount = Decimal(row[4])

        if r_from not in people:
            people[r_from] = [Decimal(0), []]

        if r_to not in people:
            people[r_to] = [Decimal(0), []]

        people[r_from][0] -= r_amount
        people[r_to][0] += r_amount
        people[r_from][1].append((r_date, r_to, r_narrative, r_amount))

    # pprint(people)
    console_prompt()


def console_prompt():
    pass


if __name__ == "__main__":
    main()
