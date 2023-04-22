from os import getenv

from certifi import where
from dotenv import load_dotenv
from MonsterLab import Monster
from pandas import DataFrame
from pymongo import MongoClient, collection


class Database:
    '''Handles the connection to the database for creating new entries,
    reseting all values, and retrieving information in a accessible form.'''

    load_dotenv()

    def _collection(self) -> collection:
        "Connect to the database and return the required collection."

        URI = getenv("DB_URI", None)
        NAME = getenv("DB_NAME", None)
        COLLECTION = getenv("DB_COLLECTION", None)

        client = MongoClient(URI,
                             tls=True,
                             tlsCAFile=where())
        return client[NAME][COLLECTION]

    def seed(self, amount: int):
        "Inserts a given amount of random Monster entries into the database."

        if not isinstance(amount, int):
            raise TypeError('can only use int (not "{}") values for the '
                            'amount'.format(amount.__class__.__name__))

        if amount < 1:
            raise ValueError('amount must be at least 1')

        monsters = iter(Monster().to_dict() for _ in range(amount))
        self._collection().insert_many(monsters)

    def reset(self):
        "Drops all records in the database."
        self._collection().drop()

    def count(self) -> int:
        "Count of entries recorded in the database."
        return self._collection().count_documents({})

    def dataframe(self) -> DataFrame:
        "Creates a dataframe object of the whole database."
        data = self._collection().find({})
        df = DataFrame(data)
        df.drop(columns=["_id"], inplace=True)
        return df

    def html_table(self) -> str:
        "Creates an HTML table of the whole database, returns None if empty."
        df = self.dataframe()

        if df.empty:
            return None

        return df.to_html()


if __name__ == '__main__':
    amount = 2048

    db = Database()
    db.reset()
    db.seed(amount)

    count = db.count()
    df = db.dataframe()
    html = db.html_table()

    assert amount == count == df.shape[0]
    assert html is not None
