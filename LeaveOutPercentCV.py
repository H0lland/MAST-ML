__author__ = 'Tam Mayeshiba'
__maintainer__ = 'Ryan Jacobs'
__version__ = '1.0'
__email__ = 'rjacobs3@wisc.edu'
__date__ = 'October 14th, 2017'

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from plot_data.PlotHelper import PlotHelper
from SingleFit import SingleFit
from SingleFit import timeit

class LeaveOutPercentCV(SingleFit):
    """Class to conduct leave out x% cross-validation analysis
   
    Args:
        training_dataset (DataHandler object): Training dataset handler
        testing_dataset (DataHandler object): Testing dataset handler
        model (sklearn model object): sklearn model
        save_path (str): Save path
        xlabel (str): Label for full-fit x-axis (default "Measured")
        ylabel (str): Label for full-fit y-axis (default "Predicted")
        mark_outlying_points (list of int): Number of outlying points to mark in best and worst tests, e.g. [0,3]

        percent_leave_out (int): Percent to leave out
        num_cvtests (int): Number of CV tests
        fix_random_for_testing (int): 
                1 - fix random shuffle for testing purposes
                0 (default) Use random shuffle
 
    Returns:
        Analysis in the save_path folder
        Plots results in a predicted vs. measured square plot.

    Raises:
        ValueError: if testing target data is None; CV must have testing target data

    """
    def __init__(self, training_dataset=None, testing_dataset=None, model=None, save_path=None, xlabel="Measured",
        ylabel="Predicted", mark_outlying_points=None, percent_leave_out=20, num_cvtests=10, fix_random_for_testing=0,
        scaler=None, *args, **kwargs):
        """
        Additional class attributes to parent class:
            Set by keyword:
            self.mark_outlying_points <list of int>: Number of outlying points in best and worst fits to mark
            self.percent_leave_out <int>: Percent to leave out of training set
                                    (becomes the percent that is tested on)
            self.num_cvtests <int>: Number of KFold tests to perform
            Set in code:
            self.cvmodel <sklearn CV model>: Cross-validation model
            self.cvtest_dict <dict>: Dictionary of CV test information and
                                        results, one entry for each cvtest.
            self.best_test_index <int>: Test number of best test
            self.worst_test_index <int>: Test number of worst test
        """
        if not(training_dataset == testing_dataset):
            raise ValueError("Only testing_dataset will be used. Use the same values for training_dataset and testing_dataset")
        SingleFit.__init__(self, 
            training_dataset=training_dataset, #only testing_dataset is used
            testing_dataset=testing_dataset,
            model=model, 
            save_path = save_path,
            xlabel=xlabel,
            ylabel=ylabel,
            scaler=scaler)
        self.mark_outlying_points = mark_outlying_points
        self.percent_leave_out = int(percent_leave_out)
        self.num_cvtests = int(num_cvtests)
        if int(fix_random_for_testing) == 1:
            np.random.seed(0)
        # Sets later in code
        self.cvmodel = None
        self.cvtest_dict=dict()
        self.best_test_index = None
        self.worst_test_index = None
        return 

    @timeit
    def set_up(self):
        SingleFit.set_up(self)
        self.set_up_cv()
        return

    @timeit
    def fit(self):
        self.cv_fit_and_predict()
        return

    @timeit
    def predict(self):
        #Predictions themselves are covered in self.fit()
        self.get_statistics()
        self.print_statistics()
        self.readme_list.append("----- Output data -----\n")
        self.print_best_worst_output_csv("best_and_worst")
        return

    @timeit
    def plot(self):
        self.readme_list.append("----- Plotting -----\n")
        notelist=list()
        notelist.append("Mean over %i LO %i%% tests:" % (self.num_cvtests, self.percent_leave_out))
        notelist.append("RMSE:")
        notelist.append("    {:.2f} $\pm$ {:.2f}".format(self.statistics['avg_rmse'], self.statistics['std_rmse']))
        notelist.append("Mean error:")
        notelist.append("    {:.2f} $\pm$ {:.2f}".format(self.statistics['avg_mean_error'], self.statistics['std_mean_error']))
        notelist.append("R-squared: " "{:.2f}".format(self.statistics['r2_score']))
        notelist.append("R-squared (no int): " "{:.2f}".format(self.statistics['r2_score_noint']))
        self.plot_best_worst_overlay(notelist=list(notelist))
        self.plot_meancv_overlay(notelist=list(notelist))
        self.plot_residuals_histogram()
        return

    def set_up_cv(self):
        if self.testing_dataset.target_data is None:
            raise ValueError("Testing target data cannot be none for cross validation.")
        indices = np.arange(0, len(self.testing_dataset.target_data))
        self.readme_list.append("----- CV setup -----\n")
        self.readme_list.append("%i CV tests,\n" % self.num_cvtests)
        self.readme_list.append("leaving out %i percent\n" % self.percent_leave_out)
        test_fraction = self.percent_leave_out / 100.0
        self.cvmodel = ShuffleSplit(n_splits = 1, 
                            test_size = test_fraction, 
                            random_state = None)
        for cvtest in range(0, self.num_cvtests):
            self.cvtest_dict[cvtest] = dict()
            for train, test in self.cvmodel.split(indices):
                fdict=dict()
                fdict['train_index'] = train
                fdict['test_index'] = test
                self.cvtest_dict[cvtest]= dict(fdict)
        return
    
    def cv_fit_and_predict(self):
        for cvtest in self.cvtest_dict.keys():
            prediction_array = np.zeros(len(self.testing_dataset.target_data))
            prediction_array[:] = np.nan
            error_array = np.zeros(len(self.testing_dataset.target_data))
            error_array[:] = np.nan

            fdict = self.cvtest_dict[cvtest]
            input_train=self.testing_dataset.input_data.iloc[fdict['train_index']]
            target_train = self.testing_dataset.target_data[fdict['train_index']]
            input_test=self.testing_dataset.input_data.iloc[fdict['test_index']]
            target_test = self.testing_dataset.target_data[fdict['test_index']]
            fit = self.model.fit(input_train, target_train)
            predict_test = self.model.predict(input_test)





            rmse = np.sqrt(mean_squared_error(predict_test, target_test))
            merr = np.mean(predict_test - target_test)
            prediction_array[fdict['test_index']] = predict_test
            error_array[fdict['test_index']] = predict_test - target_test
            self.cvtest_dict[cvtest]["rmse"] = rmse
            self.cvtest_dict[cvtest]["mean_error"] = merr
            self.cvtest_dict[cvtest]["prediction_array"] = prediction_array
            self.cvtest_dict[cvtest]["error_array"] = error_array
        return

    def get_cv_residuals(self):
        residuals = list()
        for cvtest in self.cvtest_dict.keys():
            error_list = self.cvtest_dict[cvtest]["error_array"].tolist()
            for error in error_list:
                if not np.isnan(error):
                    residuals.append(error)
        residuals = pd.DataFrame(residuals)[0]
        return residuals

    def get_statistics(self):
        cvtest_rmses = list()
        cvtest_mean_errors = list()
        for cvtest in range(0, self.num_cvtests):
            cvtest_rmses.append(self.cvtest_dict[cvtest]["rmse"])
            cvtest_mean_errors.append(self.cvtest_dict[cvtest]["mean_error"])
        highest_rmse = max(cvtest_rmses)
        self.worst_test_index = cvtest_rmses.index(highest_rmse)
        lowest_rmse = min(cvtest_rmses)
        self.best_test_index = cvtest_rmses.index(lowest_rmse)
        self.statistics['avg_rmse'] = np.mean(cvtest_rmses)
        self.statistics['std_rmse'] = np.std(cvtest_rmses)
        self.statistics['avg_mean_error'] = np.mean(cvtest_mean_errors)
        self.statistics['std_mean_error'] = np.std(cvtest_mean_errors)
        self.statistics['rmse_best'] = lowest_rmse
        self.statistics['rmse_worst'] = highest_rmse
        self.statistics['residuals'] = self.get_cv_residuals()

        # Get average CV values and errors
        average_prediction = self.cvtest_dict[0]["prediction_array"]
        average_prediction_count = ~np.isnan(average_prediction)
        average_prediction_count = average_prediction_count.astype(int)
        error = self.cvtest_dict[0]["error_array"]
        error_count = ~np.isnan(error)
        error_count = error_count.astype(int)
        for cvtest in self.cvtest_dict.keys():
            if cvtest > 0:
                for idx in range(len(average_prediction)):
                    if not np.isnan(self.cvtest_dict[cvtest]["prediction_array"][idx]):
                        average_prediction_count[idx] += 1
                    if not np.isnan(self.cvtest_dict[cvtest]["error_array"][idx]):
                        error_count[idx] += 1
                average_prediction = np.nansum(np.dstack((average_prediction,self.cvtest_dict[cvtest]["prediction_array"])),2)[0]
                error = np.vstack((error,self.cvtest_dict[cvtest]["error_array"]))
        average_prediction = average_prediction/average_prediction_count
        std_err_in_mean = np.nanstd(error, axis=0, ddof=1)/np.sqrt(error_count)

        self.statistics['std_err_in_mean'] = std_err_in_mean
        self.statistics['average_prediction'] = average_prediction

        # remove any nan from average_prediction and target data. These are points that by chance weren't ever
        # picked to be in the testing group for the CV. This is likely to happen for low number of CV tests
        stack = np.vstack((self.testing_dataset.target_data,average_prediction)).T
        stack_no_nan_columns = stack[~np.isnan(stack).any(axis=1)].T

        rsquared = self.get_rsquared(Xdata=stack_no_nan_columns[0], ydata=stack_no_nan_columns[1])
        rsquared_noint = self.get_rsquared_noint(Xdata=stack_no_nan_columns[0], ydata=stack_no_nan_columns[1])

        self.statistics['r2_score'] = rsquared
        self.statistics['r2_score_noint'] = rsquared_noint

        return

    def print_best_worst_output_csv(self, label=""):
        """
        """
        olabel = "%s_test_data.csv" % label
        ocsvname = os.path.join(self.save_path, olabel)
        self.testing_dataset.add_feature("Best Prediction", 
                    self.cvtest_dict[self.best_test_index]['prediction_array'])
        self.testing_dataset.add_feature("Worst Prediction", 
                    self.cvtest_dict[self.worst_test_index]['prediction_array'])
        cols = self.testing_dataset.print_data(ocsvname, ["Best Prediction", "Worst Prediction"])
        self.readme_list.append("%s file created with columns:\n" % olabel)
        for col in cols:
            self.readme_list.append("    %s\n" % col)
        return

    def plot_best_worst_overlay(self, notelist=list()):
        #unnormalize x before plotting
        self.testing_dataset.target_data = self.un_normalize(array=self.testing_dataset.target_data)

        kwargs2 = dict()
        kwargs2['xlabel'] = self.xlabel
        kwargs2['ylabel'] = self.ylabel
        kwargs2['labellist'] = ["Best test","Worst test"]
        kwargs2['xdatalist'] = list([self.testing_dataset.target_data, 
                            self.testing_dataset.target_data])
        kwargs2['ydatalist'] = list(
                [self.cvtest_dict[self.best_test_index]['prediction_array'],
                self.cvtest_dict[self.worst_test_index]['prediction_array']])
        kwargs2['xerrlist'] = list([None,None])
        kwargs2['yerrlist'] = list([None,None])
        kwargs2['notelist'] = list(notelist)
        kwargs2['guideline'] = 1
        kwargs2['plotlabel'] = "best_worst_overlay"
        kwargs2['save_path'] = self.save_path
        if not (self.mark_outlying_points is None):
            kwargs2['marklargest'] = self.mark_outlying_points
            if self.testing_dataset.labeling_features is None:
                raise ValueError("Must specify some labeling features if you want to mark the largest outlying points")
            labels = self.testing_dataset.data[self.testing_dataset.labeling_features[0]]
            kwargs2['mlabellist'] = list([labels,labels])
        myph = PlotHelper(**kwargs2)
        myph.multiple_overlay()
        self.readme_list.append("Plot best_worst_overlay.png created,\n")
        self.readme_list.append("    showing the best and worst of %i tests.\n" % self.num_cvtests)
        return

    def plot_meancv_overlay(self, notelist=list()):
        kwargs2 = dict()
        kwargs2['xlabel'] = self.xlabel
        kwargs2['ylabel'] = self.ylabel
        kwargs2['labellist'] = ["Mean CV test"]
        kwargs2['xdatalist'] = list([self.testing_dataset.target_data])
        kwargs2['ydatalist'] = list([self.statistics['average_prediction']])
        kwargs2['xerrlist'] = list([None])
        kwargs2['yerrlist'] = list([self.statistics['std_err_in_mean']])
        kwargs2['notelist'] = list(notelist)
        kwargs2['guideline'] = 1
        kwargs2['plotlabel'] = "mean_cv_overlay"
        kwargs2['save_path'] = self.save_path
        #kwargs2['std_err_in_mean'] = std_err_in_mean
        if not (self.mark_outlying_points is None):
            kwargs2['marklargest'] = self.mark_outlying_points
            if self.testing_dataset.labeling_features is None:
                raise ValueError("Must specify some labeling features if you want to mark the largest outlying points")
            labels = self.testing_dataset.data[self.testing_dataset.labeling_features[0]]
            kwargs2['mlabellist'] = list([labels,labels])
        myph = PlotHelper(**kwargs2)
        myph.multiple_overlay()
        self.readme_list.append("Plot mean_cv_overlay.png created,\n")
        self.readme_list.append("    showing the mean cv of %i tests.\n" % self.num_cvtests)
        return

