import csv
import logging
from decimal import *
from datetime import datetime


def main():
    people = {}
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)
    logging.info('main')

    while True:
        console_prompt(people)


def console_prompt(people):
    print("Select an option:")
    print("  (1) List all")
    print("  (2) List account")
    print("  (3) Import transactions")
    print("  (0) Exit")

    try:
        option = int(input("> "))
    except:
        return

    if option == 0:
        exit()
    elif option == 1:
        list_all(people)
    elif option == 2:
        name = str(input("Enter a name: "))
        list_account(people, name)
    elif option == 3:
        f_name = str(input("Enter a file name: "))
        import_transactions(people, f_name)

    print()


def list_all(people):
    for name, data in people.items():
        print("{0}: £{1}".format(name, data[0]))


def list_account(people, name):
    if name in people:
        data = people[name]
        print("Transactions for '{0}'".format(name))

        for tran in data[1]:
            print("  £{0} to {1} on {2:%d/%m/%Y}: '{3}'".format(
                tran[3], tran[1], tran[0], tran[2]))

    else:
        print("Name '{0}' not found".format(name))


def import_transactions(people, f_name):
    logging.info("Reading transaction data from '{0}'".format(f_name))

    try:
        with open(f_name, "r") as f:
            data = [tuple(row) for row in csv.reader(f, delimiter=',')][1:]
    except:
        logging.error("Failed to read data from file '{0}'".format(f_name))
        print("Failed to read data from file '{0}'".format(f_name))
        return

    logging.info("Importing '{0}'".format(f_name))

    total_rows = 0
    imported_rows = 0

    for i, row in enumerate(data):
        total_rows += 1
        r = i + 2  # 2 = array offset + header removed
        logging.info("Row {0}".format(r))

        try:
            r_date = datetime.strptime(row[0], "%d/%m/%Y")
        except:
            logging.error("Invalid date '{0}' on row {1}, skipping row...".format(row[0], r))
            print("Invalid date '{0}' on row {1}, skipping row...".format(row[0], r))
            continue

        r_from = row[1]
        r_to = row[2]
        r_narrative = row[3]

        try:
            r_amount = Decimal(row[4])
        except:
            logging.error("Invalid date '{0}' on row {1}, skipping row...".format(row[0], r))
            print("Invalid amount '{0}' on row {1}, skipping row...".format(row[4], r))
            continue

        if r_from not in people:
            people[r_from] = [Decimal(0), []]

        if r_to not in people:
            people[r_to] = [Decimal(0), []]

        people[r_from][0] -= r_amount
        people[r_to][0] += r_amount
        people[r_from][1].append((r_date, r_to, r_narrative, r_amount))
        imported_rows += 1

    logging.info("Imported {0} of {1} rows".format(imported_rows, total_rows))
    print("Imported {0} of {1} rows".format(imported_rows, total_rows))


if __name__ == "__main__":
    main()
