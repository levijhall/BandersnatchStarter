from pandas import DataFrame
from numpy import argmax
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
from datetime import datetime


class Machine:
    '''A class to handle the training, inference, saving, and loading of a
    Random Forest Classifier.
    '''

    def __init__(self, df: DataFrame):
        '''Train a Random Forest Classifier with optimized paramaters for the
        MonsterLab Monster Dataset.

        Keyword Arguments:
        df -- The DataFrame object containing all the values to be trained off
        of. Must contain columns for Energy, Health, Sanity, Level, and Rarity.
        '''
        features = ['Level', 'Health', 'Energy', 'Sanity']
        target = 'Rarity'

        X = df[features]
        y = df[target].values.ravel()

        self._name = "Random Forest Classifier"
        rfc = RandomForestClassifier(max_features=None)
        rfc.fit(X, y)

        self._model = rfc
        self._timestamp = datetime.now().strftime("%Y/%m/%d %I:%M:%S %p")

    def __call__(self, feature_basis: DataFrame) -> tuple[str, float]:
        '''Get the predited class and probability expected from the feature
        values.

        Keyword arguments:
        feature_basis -- the DataFrame containing a value for Health, Energy,
        Sanity, and Level.

        Returns:
        The name of the class predicted, and the probability
        infered from the model.
        '''
        pred = self._model.predict_proba(feature_basis)[0]
        index = argmax(pred)

        print(pred)

        return self._model.classes_[index], pred[index]

    def save(self, filepath):
        '''Save the instance onto the specified filepath.'''
        dump(self, filepath)

    @staticmethod
    def open(filepath):
        '''Load a fitted Machine isntance model from the filepath.'''
        return load(filepath)

    def info(self) -> str:
        '''Construct a string of the models name and a timestamp of when it was
        created seperated by an HTML break tag.

        Example:
        Base Model: Random Forest Classification
        <br>
        Timestamp: 2023/04/28 09:39:41 PM
        '''
        title = "Base Model: " + self._name
        time = "Timestamp: " + self._timestamp

        return '<br>'.join([title, time])
