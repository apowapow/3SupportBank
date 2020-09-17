from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from decimal import *
import csv
import json
import xml.etree.ElementTree as ET
from operator import itemgetter
import logging
from pprint import pprint


KEY_TOTAL = "total"
KEY_TRANSACTIONS = "transactions"
KEY_DATE = "date"
KEY_FROM = "fromAccount"
KEY_TO = "toAccount"
KEY_NARRATIVE = "narrative"
KEY_AMOUNT = "amount"

DATE_STR_FORMAT = "%Y-%m-%d"


class TransactionManager:

    def __init__(self):
        self._users = {}

    def get_users(self):
        return self._users

    def list_all(self):
        totals = [(name, data[KEY_TOTAL]) for name, data in self._users.items()]
        totals.sort(key=lambda x: x[0])

        for name, total in totals:
            print("{0}: £{1}".format(name, total))

    def list_user(self, name):
        if name in self._users:
            data = self._users[name]

            print("Transactions for '{0}'".format(name))
            data[KEY_TRANSACTIONS].sort(key=itemgetter(KEY_DATE))

            for tran in data[KEY_TRANSACTIONS]:
                print("  £{0} to {1} on {2:%d/%m/%Y}: '{3}'".format(
                    tran[KEY_AMOUNT],
                    tran[KEY_TO],
                    tran[KEY_DATE],
                    tran[KEY_NARRATIVE]))
        else:
            print("Name '{0}' not found".format(name))
            raise Exception("Name '{0}' not found".format(name))

    def add_transaction(self, user_from: str, user_to: str, amount: Decimal, date: datetime, narrative: str):
        self._maybe_create_user(user_from)
        self._maybe_create_user(user_to)

        self._users[user_from][KEY_TRANSACTIONS].append({
            KEY_TO: user_to,
            KEY_AMOUNT: amount,
            KEY_DATE: date,
            KEY_NARRATIVE: narrative
        })

        self._users[user_from][KEY_TOTAL] -= amount
        self._users[user_to][KEY_TOTAL] += amount

    def _maybe_create_user(self, name: str):
        if name not in self._users:
            self._users[name] = {KEY_TOTAL: Decimal(0), KEY_TRANSACTIONS: []}


class AbstractTransactionSource(ABC):

    _IMPORT_DATA_EXCEPTION = "File '{0}' entry {1}: invalid {2} (skipping...)"

    def __init__(self, file_name: str):
        self._file_name = file_name

    def import_data(self, manager: TransactionManager):
        logging.info("Loading '{0}'".format(self._file_name))
        for i, row in enumerate(self._read_file()):
            try:
                r_from = self._get_from(row)
            except:
                logging.info(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "from"))
                print(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "from"))
                continue

            try:
                r_to = self._get_to(row)
            except:
                logging.info(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "to"))
                print(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "to"))
                continue

            try:
                r_amount = self._get_amount(row)
            except:
                logging.info(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "amount"))
                print(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "amount"))
                continue

            try:
                r_date = self._get_date(row)
            except:
                logging.info(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "date"))
                print(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "date"))
                continue

            try:
                r_narrative = self._get_narrative(row)
            except:
                logging.info(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "narrative"))
                print(self._IMPORT_DATA_EXCEPTION.format(self._file_name, i, "narrative"))
                continue

            manager.add_transaction(r_from, r_to, r_amount, r_date, r_narrative)

    @abstractmethod
    def _read_file(self) -> List[Dict]:
        """"""

    @abstractmethod
    def _get_from(self, row: dict) -> str:
        """"""

    @abstractmethod
    def _get_to(self, row: dict) -> str:
        """"""

    @abstractmethod
    def _get_amount(self, row: dict) -> Decimal:
        """"""

    @abstractmethod
    def _get_date(self, row: dict) -> datetime:
        """"""

    @abstractmethod
    def _get_narrative(self, row: dict) -> str:
        """"""


class CSVTransactionSource(AbstractTransactionSource):

    def __init__(self, file_name: str):
        super().__init__(file_name)

    def _read_file(self) -> List[Dict]:
        with open(self._file_name, "r") as f:
            return [{
                KEY_DATE: row[0],
                KEY_FROM: row[1],
                KEY_TO: row[2],
                KEY_NARRATIVE: row[3],
                KEY_AMOUNT: row[4]
            } for row in csv.reader(f, delimiter=',')][1:]

    def _get_from(self, row: dict) -> str:
        return row[KEY_FROM]

    def _get_to(self, row: dict) -> str:
        return row[KEY_TO]

    def _get_amount(self, row: dict) -> Decimal:
        return Decimal(row[KEY_AMOUNT])

    def _get_date(self, row: dict) -> datetime:
        return datetime.strptime(row[KEY_DATE], "%d/%m/%Y")

    def _get_narrative(self, row: dict) -> str:
        return row[KEY_NARRATIVE]


class JSONTransactionSource(AbstractTransactionSource):

    def __init__(self, file_name: str):
        super().__init__(file_name)

    def _read_file(self) -> List[Dict]:
        with open(self._file_name, "r") as f:
            return [{
                KEY_DATE: row[KEY_DATE],
                KEY_FROM: row[KEY_FROM],
                KEY_TO: row[KEY_TO],
                KEY_NARRATIVE: row[KEY_NARRATIVE],
                KEY_AMOUNT: str(row[KEY_AMOUNT])
            } for row in json.loads(f.read())]

    def _get_from(self, row: dict) -> str:
        return row[KEY_FROM]

    def _get_to(self, row: dict) -> str:
        return row[KEY_TO]

    def _get_amount(self, row: dict) -> Decimal:
        return Decimal(row[KEY_AMOUNT])

    def _get_date(self, row: dict) -> datetime:
        return datetime.strptime(row[KEY_DATE], "%Y-%m-%d")

    def _get_narrative(self, row: dict) -> str:
        return row[KEY_NARRATIVE]


class XMLTransactionSource(AbstractTransactionSource):

    def __init__(self, file_name: str):
        super().__init__(file_name)

    def _read_file(self) -> List[Dict]:
        return [{
            KEY_DATE: row.attrib['Date'],
            KEY_FROM: row[2][0].text,
            KEY_TO: row[2][1].text,
            KEY_NARRATIVE: row[0].text,
            KEY_AMOUNT: row[1].text
        } for row in ET.parse(self._file_name).getroot()]

    def _get_from(self, row: dict) -> str:
        return row[KEY_FROM]

    def _get_to(self, row: dict) -> str:
        return row[KEY_TO]

    def _get_amount(self, row: dict) -> Decimal:
        return Decimal(row[KEY_AMOUNT])

    def _get_date(self, row: dict) -> datetime:
        return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(row[KEY_DATE]) - 2)

    def _get_narrative(self, row: dict) -> str:
        return row[KEY_NARRATIVE]


class TransactionSourceFactory:

    @staticmethod
    def create(file_name: str):
        if len(file_name) > 0:
            if file_name.endswith(".csv"):
                return CSVTransactionSource(file_name)

            elif file_name.endswith(".json"):
                return JSONTransactionSource(file_name)

            elif file_name.endswith(".xml"):
                return XMLTransactionSource(file_name)
        return None


class AbstractTransactionExportStrategy(ABC):

    @abstractmethod
    def export_data(self, manager: TransactionManager, file_name: str):
        """"""


class CSVExportStrategy(AbstractTransactionExportStrategy):

    def export_data(self, manager: TransactionManager, file_name: str):
        users = manager.get_users()

        with open(file_name, "w", newline="") as f:
            w = csv.DictWriter(
                f=f, fieldnames=[KEY_FROM, KEY_TO, KEY_AMOUNT, KEY_DATE, KEY_NARRATIVE])

            w.writeheader()

            for name, data in users.items():
                for trans in data[KEY_TRANSACTIONS]:
                    write_dict = {**{KEY_FROM: name}, **trans}
                    write_dict[KEY_DATE] = write_dict[KEY_DATE].strftime(DATE_STR_FORMAT)
                    w.writerow(write_dict)


class JSONExportStrategy(AbstractTransactionExportStrategy):

    def export_data(self, manager: TransactionManager, file_name: str):
        return False


class XMLExportStrategy(AbstractTransactionExportStrategy):

    def export_data(self, manager: TransactionManager, file_name: str):
        return False


class TransactionExportFactory:

    @staticmethod
    def create(file_name: str):
        if len(file_name) > 0:
            if file_name.endswith(".csv"):
                return CSVExportStrategy()

            elif file_name.endswith(".json"):
                return JSONExportStrategy()

            elif file_name.endswith(".xml"):
                return XMLExportStrategy()
        return None
