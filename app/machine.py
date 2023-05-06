from pandas import DataFrame
from numpy import argmax, std
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
        z = df[
            ['Rarity', 'Level', 'Health', 'Energy', 'Sanity']
            ].groupby(
            ['Rarity', 'Level']
            ).aggregate(std).reset_index()
        z_mean = z[
            ['Rarity', 'Health', 'Energy', 'Sanity']
            ].groupby(
            ['Rarity']
            ).mean()
        self.z_mean = z_mean

        X = self.make_features(df)
        y = df['Rarity'].values.ravel()

        self._name = "Random Forest Classifier"
        rfc = RandomForestClassifier(max_features=None,
                                     n_estimators=300,
                                     max_depth=10)
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

        df_feat = self.make_features(feature_basis)
        pred = self._model.predict_proba(df_feat)[0]
        index = argmax(pred)

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

    def make_features(self, df: DataFrame) -> DataFrame:
        '''Generate the engineered features.

        Keyword arguments:
        df -- the DataFrame containing the values for Rarity, Health, Energy,
        Sanity, and Level.

        Returns:
        A DataFrame containing several additional columns for Health, Energy,
        and Sanity, suffixed with _z_(r) where 'r' corresponds with the
        Rarity Rank number and is calculated to be the standard deviation away
        from the mean value for a monster of that Level and Rarity.
        '''

        df_feat = DataFrame()
        df_feat['Level'] = df['Level']

        ranks = [0, 1, 2, 3, 4, 5]
        params = ['Health', 'Energy', 'Sanity']
        new_features = []

        for param in params:
            for rank in ranks:
                name = param + "_z_" + str(rank)
                new_features.append(name)
                lookup = self.z_mean[param].to_dict()

                df_feat[name] = abs(df[param] - 2 * df['Level'] * (rank + 1)) \
                    / lookup['Rank ' + str(rank)]

        return df_feat
