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
    while True:
        console_prompt(people)


def console_prompt(people):
    print("Select an option:\n (1) List all\n (2) List account\n (0) Exit")
    option = int(input("> "))

    if option == 0:
        exit()
    elif option == 1:
        list_all(people)
    elif option == 2:
        name = str(input("Enter a name: "))
        list_account(people, name)
        pass

    print()


def list_all(people):
    for name, data in people.items():
        print("{0}: £{1}".format(name, data[0]))


def list_account(people, name):
    if name in people:
        data = people[name]
        print("Transactions for '{0}'".format(name))

        for tran in data[1]:
            print("  £{0} to {1} on {2}: '{3}'".format(
                tran[3], tran[1], tran[0], tran[2]))

    else:
        print("Name '{0}' not found".format(name))


if __name__ == "__main__":
    main()
