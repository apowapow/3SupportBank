import logging
from trans import *


OPTION_EXIT = 0
OPTION_LIST_ALL = 1
OPTION_LIST_ACCOUNT = 2
OPTION_IMPORT_TRANSACTIONS = 3
OPTION_EXPORT_TRANSACTIONS = 4


def main():
    manager = TransactionManager()

    logging.basicConfig(filename='SupportBank.log',
                        filemode='w',
                        level=logging.DEBUG)
    logging.info('main')

    while True:
        try:
            console_prompt(manager)
        except Exception as e:
            print("Error: {0}".format(str(e)))
            logging.error(str(e))


def console_prompt(manager: TransactionManager):
    print("Select an option:")
    print("  (1) List all")
    print("  (2) List account")
    print("  (3) Import transactions")
    print("  (4) Export transactions")
    print("  (0) Exit")

    option = get_int_input("> ", OPTION_EXIT, OPTION_EXPORT_TRANSACTIONS)

    if option == OPTION_EXIT:
        exit()

    elif option == OPTION_LIST_ALL:
        manager.list_all()

    elif option == OPTION_LIST_ACCOUNT:
        manager.list_user(
            get_str_input("Enter a name: "))

    elif option == OPTION_IMPORT_TRANSACTIONS:
        file_name = get_str_input("Enter import file name: ")
        source = TransactionSourceFactory.create(file_name)

        if source is not None:
            source.import_data(manager)
        else:
            print("File '{0}' is an unsupported type".format(file_name))

    elif option == OPTION_EXPORT_TRANSACTIONS:
        file_name = get_str_input("Enter export file name: ")
        exporter = TransactionExportFactory.create(file_name)

        if exporter is not None:
            logging.info("Exporter: {0}".format(exporter.__class__.__name__))
            exporter.export_data(manager, file_name)
        else:
            print("File '{0}' is an unsupported type".format(file_name))

    print()


def get_int_input(text: str, input_min: int, input_max: int) -> int:
    user_input = None

    while user_input is None:
        try:
            user_input = int(input(text))

            if not (input_min <= user_input <= input_max):
                user_input = None
        except:
            user_input = None
            print("Input must be between {0}-{1} (inclusive)".format(input_min, input_max))

    return user_input


def get_str_input(text: str, len_min: int=1) -> str:
    user_input = None

    while user_input is None:
        try:
            user_input = input(text)

            if len(user_input) < len_min:
                user_input = None
        except:
            user_input = None
            print("Input must be at least {0} in length".format(len_min))

    return user_input


if __name__ == "__main__":
    main()
