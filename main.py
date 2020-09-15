import csv
import json
import logging
from decimal import *
from datetime import datetime


K_TOTAL = "total"
K_TRANSACTIONS = "transactions"
K_DATE = "date"
K_FROM = "fromAccount"
K_TO = "toAccount"
K_NARRATIVE = "narrative"
K_AMOUNT = "amount"

KNOWN_DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d"]


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
        print("{0}: £{1}".format(name, data[K_TOTAL]))


def list_account(people, name):
    if name in people:
        data = people[name]
        print("Transactions for '{0}'".format(name))

        for tran in data[K_TRANSACTIONS]:
            print("  £{0} to {1} on {2:%d/%m/%Y}: '{3}'".format(
                tran[K_AMOUNT], tran[K_TO], tran[K_DATE], tran[K_NARRATIVE]))
    else:
        print("Name '{0}' not found".format(name))


def import_transactions(people, f_name):
    logging.info("Reading transaction data from '{0}'".format(f_name))

    if f_name.endswith(".csv"):
        data = read_csv_data(f_name)
    elif f_name.endswith(".json"):
        data = read_json_data(f_name)
    elif f_name.endswith(".xml"):
        data = read_xml_data(f_name)
    else:
        logging.error("File '{0}' has unsupported type".format(f_name))
        print("File '{0}' has unsupported type".format(f_name))
        return

    if data is None:
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

        r_date = get_date_from_str(row[K_DATE])
        if r_date is None:
            logging.error("Invalid date '{0}' on row {1}, skipping row...".format(row[K_DATE], r))
            print("Invalid date '{0}' on row {1}, skipping row...".format(row[K_DATE], r))
            continue

        r_from = row[K_FROM]
        r_to = row[K_TO]
        r_narrative = row[K_NARRATIVE]

        try:
            r_amount = Decimal(row[K_AMOUNT])
        except:
            logging.error("Invalid amount '{0}' on row {1}, skipping row...".format(row[K_AMOUNT], r))
            print("Invalid amount '{0}' on row {1}, skipping row...".format(row[K_AMOUNT], r))
            continue

        if r_from not in people:
            people[r_from] = {K_TOTAL: Decimal(0), K_TRANSACTIONS: []}

        if r_to not in people:
            people[r_to] = {K_TOTAL: Decimal(0), K_TRANSACTIONS: []}

        people[r_from][K_TOTAL] -= r_amount
        people[r_to][K_TOTAL] += r_amount
        people[r_from][K_TRANSACTIONS].append({
            K_DATE: r_date,
            K_TO: r_to,
            K_NARRATIVE: r_narrative,
            K_AMOUNT: r_amount})
        imported_rows += 1

    logging.info("Imported {0} of {1} rows".format(imported_rows, total_rows))
    print("Imported {0} of {1} rows".format(imported_rows, total_rows))


def get_date_from_str(str_date):
    for kdf in KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(str_date, kdf)
        except:
            continue

def read_csv_data(f_name):
    try:
        with open(f_name, "r") as f:
            data = [{
                K_DATE: row[0],
                K_FROM: row[1],
                K_TO: row[2],
                K_NARRATIVE: row[3],
                K_AMOUNT: row[4]
            } for row in csv.reader(f, delimiter=',')][1:]
    except:
        return None
    return data


def read_json_data(f_name):
    try:
        with open(f_name, "r") as f:
            data = [{
                K_DATE: row[K_DATE],
                K_FROM: row[K_FROM],
                K_TO: row[K_TO],
                K_NARRATIVE: row[K_NARRATIVE],
                K_AMOUNT: str(row[K_AMOUNT])
            } for row in json.loads(f.read())]
    except:
        return None
    return data


def read_xml_data(f_name):
    return None  # todo


if __name__ == "__main__":
    main()
