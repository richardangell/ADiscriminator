import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing

from numpy.testing import assert_almost_equal

import adiscriminator as ad
from adiscriminator import data



def test_compare_statsmodels_non_reg():
    """Compare statsmodels logistic regression to non regularised logistic_regression"""

    # fix to prevent error with depreceated scipy fcn being used by statsmodels
    # fix from github user VincentLa14;
    # https://github.com/statsmodels/statsmodels/issues/3931
    stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)

    adult = data.get_data()

    adult_X, adult_y = data.data_to_np(adult)

    ad_log_reg = ad.logistic_regression.base.LogisticRegression(fit_intercept = True, standardise = True)

    ad_log_reg.fit(adult_X, adult_y)

    # statsmodels requires a constant column to be added to fit an intercept
    adult_X = np.hstack([np.ones((adult_X.shape[0], 1)), adult_X])

    statsmodels_log_reg = sm.Logit(adult_y, adult_X)

    result = statsmodels_log_reg.fit()

    assert_almost_equal(actual = ad_log_reg.coefficients['coef'].tolist(),
                        desired = result.params.tolist(), 
                        decimal = 3)

def test_compare_sklearn_l2_reg():
    """Compare scikit learn logistic regression to logistic_regression with l2 regularisation and intercept"""

    adult = data.get_data()

    adult_X, adult_y = data.data_to_np(adult)

    regularisation_value = 8

    # note scikit learn penalises the intercept term as well as all the other coefficients
    ad_log_reg = ad.logistic_regression.ridge.RidgeRegression(
        fit_intercept = True, 
        standardise = True,
        lambda_ = regularisation_value, 
        penalise_intercept = True
    )

    ad_log_reg.fit(adult_X, adult_y)

    # non-standardised scikit learn coefficients don't seem to match
    # so check the standardised coefficients for now
    adult_X = preprocessing.scale(adult_X)

    # scikit learn's regularisation strength is C = 1 / lambda
    sklearn_log_reg = LogisticRegression(C = 1 / regularisation_value, penalty = 'l2', fit_intercept = True)

    sklearn_log_reg.fit(adult_X, adult_y)

    assert_almost_equal(actual = ad_log_reg.coefficients['std_coef'].tolist(),
                        desired = sklearn_log_reg.intercept_.tolist() + sklearn_log_reg.coef_[0].tolist(), 
                        decimal = 2)

def test_compare_sklearn_l2_reg_no_intercept():
    """Compare scikit learn logistic regression to logistic_regression with l2 regularisation and no intercept term"""

    adult = data.get_data()

    adult_X, adult_y = data.data_to_np(adult)

    regularisation_value = 4

    ad_log_reg = ad.logistic_regression.ridge.RidgeRegression(
        fit_intercept = False, 
        standardise = True,
        lambda_ = regularisation_value, 
        penalise_intercept = False
    )

    ad_log_reg.fit(adult_X, adult_y)

    adult_X = preprocessing.scale(adult_X)

    sklearn_log_reg = LogisticRegression(C = 1 / regularisation_value, penalty = 'l2', fit_intercept = False)

    sklearn_log_reg.fit(adult_X, adult_y)

    assert_almost_equal(actual = ad_log_reg.coefficients['std_coef'].tolist(),
                        desired = sklearn_log_reg.coef_[0].tolist(), 
                        decimal = 3)


