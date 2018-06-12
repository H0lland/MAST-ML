__author__ = 'Ryan Jacobs, Tam Mayeshiba'
__maintainer__ = 'Ryan Jacobs'
__version__ = '1.0'
__email__ = 'rjacobs3@wisc.edu'
__date__ = 'October 14th, 2017'

import sys
import os
import importlib
import logging
from sklearn.kernel_ridge import KernelRidge
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.linear_model import LinearRegression, Lasso, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, AdaBoostRegressor, ExtraTreesClassifier, RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.svm import SVC, SVR
import sklearn.gaussian_process.kernels as skkernel
from sklearn.gaussian_process import GaussianProcessRegressor
from configobj import ConfigObj, ConfigObjError
import distutils.util as du

class ConfigFileParser(object):
    """
    Class to read in contents of MASTML input files

    Args:
        configfile (MASTML configfile object) : a MASTML input file, as a configfile object

    Methods:
        get_config_dict : returns dict representation of configfile

            Args:
                path_to_file (str) : path indicating where config file is stored

            Returns:
                dict : configdict of parsed input file
    """
    def __init__(self, configfile):
        self.configfile = configfile

    def get_config_dict(self, path_to_file):
        return self._parse_config_file(path_to_file=path_to_file)

    def _get_config_dict_depth(self, test_dict, level=0):
        if not isinstance(test_dict, dict) or not test_dict:
            return level
        return max(self._get_config_dict_depth(test_dict=test_dict[k], level=level+1) for k in test_dict)

    def _parse_config_file(self, path_to_file):
        if not os.path.exists(path_to_file):
            logging.info('You must specify a valid path')
            sys.exit()
        if os.path.exists(path_to_file+"/"+str(self.configfile)):
            original_dir = os.getcwd()
            os.chdir(path_to_file)
            try:
                config_dict = ConfigObj(self.configfile)
                os.chdir(original_dir)
                return config_dict
            except(ConfigObjError, IOError):
                logging.info('Could not read in input file %s') % str(self.configfile)
                sys.exit()
        else:
            raise OSError('The input file you specified, %s, does not exist in the path %s' % (str(self.configfile), str(path_to_file)))

class ConfigFileConstructor(ConfigFileParser):
    """
    Constructor class to build input file template. Used for input file validation and data type casting.

    Args:
        configfile (MASTML configfile object) : a MASTML input file, as a configfile object

    Methods:
        get_config_template : returns template of input file for validation

            Returns:
                dict : configdict of template input file
    """
    def __init__(self, configfile):
        super().__init__(configfile=configfile)
        self.configtemplate = dict()

    def get_config_template(self):
        self._general_setup()
        self._data_setup()
        self._feature_normalization()
        self._feature_generation()
        self._feature_selection()
        self._models_and_tests_to_run()
        self._test_parameters()
        self._model_parameters()
        return self.configtemplate

    def _general_setup(self):
        self.configtemplate['General Setup'] = dict()
        self.configtemplate['General Setup']['save_path'] = 'string'
        self.configtemplate['General Setup']['input_features'] = ['string', 'string_list', 'Auto']
        self.configtemplate['General Setup']['target_feature'] = 'string'
        self.configtemplate['General Setup']['grouping_feature'] = 'string'
        self.configtemplate['General Setup']['labeling_features'] = ['string']
        return

    def _data_setup(self):
        self.configtemplate['Data Setup'] = dict()
        self.configtemplate['Data Setup']['string'] = dict()
        self.configtemplate['Data Setup']['string']['data_path'] = 'string'
        return

    def _feature_normalization(self):
        self.configtemplate['Feature Normalization'] = dict()
        self.configtemplate['Feature Normalization']['normalize_x_features'] = 'bool'
        self.configtemplate['Feature Normalization']['normalize_y_feature'] = 'bool'
        self.configtemplate['Feature Normalization']['feature_normalization_type'] = ['standardize', 'normalize']
        self.configtemplate['Feature Normalization']['feature_scale_min'] = 'float'
        self.configtemplate['Feature Normalization']['feature_scale_max'] = 'float'
        return

    def _feature_generation(self):
        self.configtemplate['Feature Generation'] = dict()
        self.configtemplate['Feature Generation']['perform_feature_generation'] = 'bool'
        self.configtemplate['Feature Generation']['add_magpie_features'] = 'bool'
        self.configtemplate['Feature Generation']['add_materialsproject_features'] = 'bool'
        self.configtemplate['Feature Generation']['add_citrine_features'] = 'bool'
        self.configtemplate['Feature Generation']['materialsproject_apikey'] = 'string'
        self.configtemplate['Feature Generation']['citrine_apikey'] = 'string'
        return

    def _feature_selection(self):
        self.configtemplate['Feature Selection'] = dict()
        self.configtemplate['Feature Selection']['perform_feature_selection'] = 'bool'
        self.configtemplate['Feature Selection']['remove_constant_features'] = 'bool'
        self.configtemplate['Feature Selection']['feature_selection_algorithm'] = ['univariate_feature_selection',
                                                                                   'recursive_feature_elimination',
                                                                                   'sequential_forward_selection',
                                                                                   'basic_forward_selection']
        self.configtemplate['Feature Selection']['use_mutual_information'] = 'bool'
        self.configtemplate['Feature Selection']['number_of_features_to_keep'] = 'integer'
        self.configtemplate['Feature Selection']['scoring_metric'] = ['mean_squared_error', 'mean_absolute_error',
                                                                      'root_mean_squared_error', 'r2_score']
        self.configtemplate['Feature Selection']['generate_feature_learning_curve'] = 'bool'
        self.configtemplate['Feature Selection']['model_to_use_for_learning_curve'] = ['linear_model_regressor',
                                                                                       'linear_model_lasso_regressor',
                                                                                       'lkrr_model_regressor',
                                                                                       'gkrr_model_regressor',
                                                                                       'support_vector_machine_model_regressor',
                                                                                       'decision_tree_model_regressor',
                                                                                       'extra_trees_model_regressor',
                                                                                       'randomforest_model_regressor',
                                                                                       'adaboost_model_regressor',
                                                                                       'nn_model_regressor',
                                                                                       'gaussianprocess_model_regressor']

        return

    def _models_and_tests_to_run(self):
        self.configtemplate['Models and Tests to Run'] = dict()
        self.configtemplate['Models and Tests to Run']['models'] = ['linear_model_regressor',
                                                                    'linear_model_lasso_regressor',
                                                                    'gkrr_model_regressor',
                                                                    'support_vector_machine_model_regressor',
                                                                    'decision_tree_model_regressor',
                                                                    'extra_trees_model_regressor',
                                                                    'randomforest_model_regressor',
                                                                    'adaboost_model_regressor',
                                                                    'nn_model_regressor',
                                                                    'gaussianprocess_model_regressor']
        self.configtemplate['Models and Tests to Run']['test_cases'] = ['SingleFit', 'SingleFitPerGroup', 'SingleFitGrouped',
                                                                        'KFoldCV', 'LeaveOneOutCV', 'LeaveOutPercentCV',
                                                                        'LeaveOutGroupCV', 'PredictionVsFeature',
                                                                        'PlotNoAnalysis', 'ParamGridSearch', 'ParamOptGA']
        return

    def _test_parameters(self):
        self.configtemplate['Test Parameters'] = dict()
        for test_case in self.configtemplate['Models and Tests to Run']['test_cases']:
            self.configtemplate['Test Parameters'][test_case] = dict()
        for k in self.configtemplate['Test Parameters'].keys():
            if k in ['SingleFit', 'SingleFitPerGroup', 'SingleFitGrouped', 'KFoldCV', 'LeaveOneOutCV', 'LeaveOutPercentCV',
                     'LeaveOutGroupCV', 'PlotNoAnalysis', 'PredictionVsFeature']:
                self.configtemplate['Test Parameters'][k]['training_dataset'] = 'string'
                self.configtemplate['Test Parameters'][k]['testing_dataset'] = 'string'
                self.configtemplate['Test Parameters'][k]['xlabel'] = 'string'
                self.configtemplate['Test Parameters'][k]['ylabel'] = 'string'
            if k in ['PlotNoAnalysis', 'PredictionVsFeature']:
                self.configtemplate['Test Parameters'][k]['feature_plot_feature'] = 'string'
                self.configtemplate['Test Parameters'][k]['plot_filter_out'] = 'string'
                self.configtemplate['Test Parameters'][k]['data_labels'] = 'string'
            if k == 'SingleFit':
                self.configtemplate['Test Parameters'][k]['plot_filter_out'] = 'string'
            if k == 'SingleFitPerGroup':
                self.configtemplate['Test Parameters'][k]['plot_filter_out'] = 'string'
            if k == 'SingleFitGrouped':
                self.configtemplate['Test Parameters'][k]['plot_filter_out'] = 'string'
            if k in ['KFoldCV', 'LeaveOneOutCV', 'LeaveOutPercentCV', 'LeaveOutGroupCV']:
                self.configtemplate['Test Parameters'][k]['num_cvtests'] = 'integer'
                self.configtemplate['Test Parameters'][k]['mark_outlying_points'] = 'integer'
            if k == 'KFoldCV':
                self.configtemplate['Test Parameters'][k]['num_folds'] = 'integer'
            if k == 'LeaveOutPercentCV':
                self.configtemplate['Test Parameters'][k]['percent_leave_out'] = 'float'
            if k in ['ParamOptGA', 'ParamGridSearch']:
                self.configtemplate['Test Parameters'][k]['training_dataset'] = 'string'
                self.configtemplate['Test Parameters'][k]['testing_dataset'] = 'string'
                self.configtemplate['Test Parameters'][k]['num_folds'] = 'integer'
                self.configtemplate['Test Parameters'][k]['num_cvtests'] = 'integer'
                self.configtemplate['Test Parameters'][k]['percent_leave_out'] = 'float'
                self.configtemplate['Test Parameters'][k]['pop_upper_limit'] = 'integer'
                for i in range(5):
                    self.configtemplate['Test Parameters'][k]['param_%s' % str(i+1)] = 'string'
        return

    def _model_parameters(self):
        self.configtemplate['Model Parameters'] = dict()
        models = [k for k in self.configtemplate['Models and Tests to Run']['models']]
        for model in models:
            self.configtemplate['Model Parameters'][model] = dict()
        for k in self.configtemplate['Model Parameters'].keys():
            if k in ['linear_model_regressor', 'linear_model_lasso_regressor']:
                self.configtemplate['Model Parameters'][k]['fit_intercept'] = 'bool'
            if k == 'linear_model_lasso_regressor':
                self.configtemplate['Model Parameters'][k]['alpha'] = 'float'
            if k == 'gkrr_model_regressor':
                self.configtemplate['Model Parameters'][k]['alpha'] = 'float'
                self.configtemplate['Model Parameters'][k]['gamma'] = 'float'
                self.configtemplate['Model Parameters'][k]['coef0'] = 'float'
                self.configtemplate['Model Parameters'][k]['degree'] = 'integer'
                self.configtemplate['Model Parameters'][k]['kernel'] = ['linear', 'cosine', 'polynomial', 'sigmoid', 'rbf', 'laplacian']
            if k == 'support_vector_machine_model_regressor':
                self.configtemplate['Model Parameters'][k]['error_penalty'] = 'float'
                self.configtemplate['Model Parameters'][k]['gamma'] = 'float'
                self.configtemplate['Model Parameters'][k]['coef0'] = 'float'
                self.configtemplate['Model Parameters'][k]['degree'] = 'integer'
                self.configtemplate['Model Parameters'][k]['kernel'] = ['linear', 'cosine', 'polynomial', 'sigmoid', 'rbf', 'laplacian']
            if k == 'decision_tree_model_regressor':
                self.configtemplate['Model Parameters'][k]['criterion'] = ['mae', 'mse', 'friedman_mse']
                self.configtemplate['Model Parameters'][k]['splitter'] = ['random', 'best']
                self.configtemplate['Model Parameters'][k]['max_depth'] = 'integer'
                self.configtemplate['Model Parameters'][k]['min_samples_leaf'] = 'integer'
                self.configtemplate['Model Parameters'][k]['min_samples_split'] = 'integer'
            if k in ['extra_trees_model_regressor', 'randomforest_model_regressor']:
                self.configtemplate['Model Parameters'][k]['criterion'] = ['mse', 'mae']
                self.configtemplate['Model Parameters'][k]['n_estimators'] = 'integer'
                self.configtemplate['Model Parameters'][k]['max_depth'] = 'integer'
                self.configtemplate['Model Parameters'][k]['min_samples_leaf'] = 'integer'
                self.configtemplate['Model Parameters'][k]['min_samples_split'] = 'integer'
                self.configtemplate['Model Parameters'][k]['max_leaf_nodes'] = 'integer'
            if k == 'randomforest_model_regressor':
                self.configtemplate['Model Parameters'][k]['n_jobs'] = 'integer'
                self.configtemplate['Model Parameters'][k]['warm_start'] = 'bool'
            if k == 'adaboost_model_regressor':
                self.configtemplate['Model Parameters'][k]['base_estimator_max_depth'] = 'integer'
                self.configtemplate['Model Parameters'][k]['n_estimators'] = 'integer'
                self.configtemplate['Model Parameters'][k]['learning_rate'] = 'float'
                self.configtemplate['Model Parameters'][k]['loss'] = ['linear' 'square', 'exponential']
            if k == 'nn_model_regressor':
                self.configtemplate['Model Parameters'][k]['hidden_layer_sizes'] = 'tuple'
                self.configtemplate['Model Parameters'][k]['activation'] = ['identity', 'logistic', 'tanh', 'relu']
                self.configtemplate['Model Parameters'][k]['solver'] = ['lbfgs', 'sgd', 'adam']
                self.configtemplate['Model Parameters'][k]['alpha'] = 'float'
                self.configtemplate['Model Parameters'][k]['max_iterations'] = 'integer'
                self.configtemplate['Model Parameters'][k]['tolerance'] = 'float'
            if k == 'gaussianprocess_model_regressor':
                self.configtemplate['Model Parameters'][k]['kernel'] = ['rbf']
                self.configtemplate['Model Parameters'][k]['RBF_length_scale'] = 'float'
                self.configtemplate['Model Parameters'][k]['RBF_length_scale_bounds'] = 'tuple'
                self.configtemplate['Model Parameters'][k]['alpha'] = 'float'
                self.configtemplate['Model Parameters'][k]['optimizer'] = ['fmin_l_bfgs_b']
                self.configtemplate['Model Parameters'][k]['n_restarts_optimizer'] = 'integer'
                self.configtemplate['Model Parameters'][k]['normalize_y'] = 'bool'
        return

class ConfigFileValidator(ConfigFileConstructor, ConfigFileParser):
    """
    Class to validate contents of user-specified MASTML input file and flag any errors

    Args:
        configfile (MASTML configfile object) : a MASTML input file, as a configfile object

    Methods:
        run_config_validation : checks configfile object for errors

            Returns:
                dict : configdict of parsed input file
                bool : whether any errors occurred parsing the input file
    """
    def __init__(self, configfile):
        super().__init__(configfile)
        self.get_config_template()

    def run_config_validation(self):
        errors_present = False
        configdict = self.get_config_dict(path_to_file=os.getcwd())

        # Check section names
        logging.info('MASTML is checking that the section names of your input file are valid...')
        configdict, errors_present = self._check_config_section_names(configdict=configdict, errors_present=errors_present)
        self._check_for_errors(errors_present=errors_present)
        logging.info('MASTML input file section names are valid')

        # Check subsection names
        logging.info('MASTML is checking that the subsection names and values in your input file are valid...')
        errors_present = self._check_config_subsection_names(configdict=configdict, errors_present=errors_present)
        self._check_for_errors(errors_present=errors_present)
        logging.info('MASTML input file subsection names are valid')

        logging.info('MASTML is checking your subsection parameter values and converting the datatypes of values in your input file...')
        configdict, errors_present = self._check_config_subsection_values(configdict=configdict, errors_present=errors_present)
        self._check_for_errors(errors_present=errors_present)
        logging.info('MASTML subsection parameter values converted to correct datatypes, and parameter keywords are valid')

        logging.info('MASTML is cross-checking model and test_case names in your input file...')
        configdict, errors_present = self._check_config_heading_compatibility(configdict=configdict, errors_present=errors_present)
        self._check_for_errors(errors_present=errors_present)
        logging.info('MASTML model and test_case names are valid')

        logging.info('MASTML is checking that your target feature name is formatted correctly...')
        configdict, errors_present = self._check_target_feature(configdict=configdict, errors_present=errors_present)
        self._check_for_errors(errors_present=errors_present)
        logging.info('MASTML target feature name is valid')

        return configdict, errors_present

    def _check_config_section_names(self, configdict, errors_present):
        # Check if extra sections are in input file that shouldn't be
        for k in configdict.keys():
            if k not in self.configtemplate.keys():
                logging.info('Error: You have an extra section called %s in your input file. To correct this issue, remove this extra section.' % str(k))
                errors_present = bool(True)

        # Check if any sections are missing from input file
        for k in self.configtemplate.keys():
            if k not in configdict.keys():
                logging.info('Error: You are missing the section called %s in your input file. To correct this issue, add this section to your input file.' % str(k))
                errors_present = bool(True)

        return configdict, errors_present

    def _check_config_subsection_names(self, configdict, errors_present):
        for section in self.configtemplate.keys():
            depth = self._get_config_dict_depth(test_dict=self.configtemplate[section])
            if depth == 1:
                # Check that required subsections are present for each section in user's input file.
                for section_key in self.configtemplate[section].keys():
                    if section_key not in configdict[section].keys():
                        logging.info('Error: Your input file is missing section key %s, which is part of the %s section. Please include this section key in your input file.' % (section_key, section))
                        errors_present = bool(True)
                # Check that user's input file does not have any extra section keys that would later throw errors
                for section_key in configdict[section].keys():
                    if section_key not in self.configtemplate[section].keys():
                        logging.info('Error: Your input file contains an extra section key or misspelled section key: %s in the %s section. Please correct this section key in your input file.' % (section_key, section))
                        errors_present = bool(True)
            if depth == 2:
                # Check that all subsections in input file are appropriately named. Note that not all subsections in template need to be present in input file
                for subsection_key in configdict[section].keys():
                    if section == 'Data Setup':
                        if not (type(subsection_key) == str):
                            errors_present = bool(True)
                    if section == 'Test Parameters':
                        if '_' in subsection_key:
                            if not (subsection_key.split('_')[0] in self.configtemplate[section]):
                                logging.info('Error: Your input file contains an improper subsection key name: %s.' % subsection_key)
                                errors_present = bool(True)
                        else:
                            if not (subsection_key in self.configtemplate[section]):
                                logging.info('Error: Your input file contains an improper subsection key name: %s.' % subsection_key)
                                errors_present = bool(True)
                    if section == 'Model Parameters':
                        if not (subsection_key in self.configtemplate[section]):
                            logging.info('Error: Your input file contains an improper subsection key name: %s.' % subsection_key)
                            errors_present = bool(True)

                    for subsection_param in configdict[section][subsection_key]:
                        if section == 'Data Setup':
                            subsection_key = 'string'
                        if section == 'Test Parameters':
                            if '_' in subsection_key:
                                subsection_key = subsection_key.split('_')[0]
                        try:
                            if not (subsection_param in self.configtemplate[section][subsection_key]):
                                logging.info('Error: Your input file contains an improper subsection parameter name: %s.' % subsection_param)
                                errors_present = bool(True)
                        except KeyError:
                            logging.info('Error: Your input file contains an improper subsection key name: %s.' % subsection_key)
                            errors_present = bool(True)

            elif depth > 2:
                logging.info('There is an error in your input file setup: too many subsections.')
                errors_present = bool(True)

        self._check_for_errors(errors_present=errors_present)

        return errors_present

    def _check_config_subsection_values(self, configdict, errors_present):
        # First do some manual cleanup for values that can be string or list
        def string_to_list(configdict):
            for section_heading in configdict.keys():
                if section_heading == 'General Setup':
                    if type(configdict[section_heading]['input_features']) is str:
                        templist = list()
                        templist.append(configdict[section_heading]['input_features'])
                        configdict[section_heading]['input_features'] = templist
                    if type(configdict[section_heading]['labeling_features']) is str:
                        templist = list()
                        templist.append(configdict[section_heading]['labeling_features'])
                        configdict[section_heading]['labeling_features'] = templist
                if section_heading == 'Models and Tests to Run':
                    if type(configdict[section_heading]['models']) is str:
                        templist = list()
                        templist.append(configdict[section_heading]['models'])
                        configdict[section_heading]['models'] = templist
                    if type(configdict[section_heading]['test_cases']) is str:
                        templist = list()
                        templist.append(configdict[section_heading]['test_cases'])
                        configdict[section_heading]['test_cases'] = templist
            return configdict

        configdict = string_to_list(configdict=configdict)
        for section in configdict.keys():
            depth = self._get_config_dict_depth(test_dict=configdict[section])
            if depth == 1:
                for section_key in configdict[section].keys():
                    if type(self.configtemplate[section][section_key]) is str:
                        if self.configtemplate[section][section_key] == 'string':
                            configdict[section][section_key] = str(configdict[section][section_key])
                        elif self.configtemplate[section][section_key] == 'bool':
                            configdict[section][section_key] = bool(du.strtobool(configdict[section][section_key]))
                        elif self.configtemplate[section][section_key] == 'integer':
                            configdict[section][section_key] = int(configdict[section][section_key])
                        elif self.configtemplate[section][section_key] == 'float':
                            configdict[section][section_key] = float(configdict[section][section_key])
                        else:
                            logging.info('Error: Unrecognized data type encountered in input file template')
                            sys.exit()
                    elif type(self.configtemplate[section][section_key]) is list:
                        if type(configdict[section][section_key]) is str:
                            if configdict[section][section_key] not in self.configtemplate[section][section_key]:
                                logging.info('Error: Your input file contains an incorrect parameter keyword: %s' % str(configdict[section][section_key]))
                                errors_present = bool(True)
                        if type(configdict[section][section_key]) is list:
                            for param_value in configdict[section][section_key]:
                                if section_key == 'test_cases':
                                    if '_' in param_value:
                                        param_value = param_value.split('_')[0]
                                    if param_value not in self.configtemplate[section][section_key]:
                                        logging.info('Error: Your input file contains an incorrect parameter keyword: %s' % param_value)
                                        errors_present = bool(True)
            if depth == 2:
                for subsection_key in configdict[section].keys():
                    for param_name in configdict[section][subsection_key].keys():
                        subsection_key_template = subsection_key
                        if section == 'Data Setup':
                            subsection_key_template = 'string'
                        elif section == 'Test Parameters':
                            if '_' in subsection_key:
                                subsection_key_template = subsection_key.split('_')[0]
                        if type(self.configtemplate[section][subsection_key_template][param_name]) is str:
                            if self.configtemplate[section][subsection_key_template][param_name] == 'string':
                                configdict[section][subsection_key][param_name] = str(configdict[section][subsection_key][param_name])
                            if self.configtemplate[section][subsection_key_template][param_name] == 'bool':
                                configdict[section][subsection_key][param_name] = bool(du.strtobool(configdict[section][subsection_key][param_name]))
                            if self.configtemplate[section][subsection_key_template][param_name] == 'integer':
                                configdict[section][subsection_key][param_name] = int(configdict[section][subsection_key][param_name])
                            if self.configtemplate[section][subsection_key_template][param_name] == 'float':
                                configdict[section][subsection_key][param_name] = float(configdict[section][subsection_key][param_name])
        return configdict, errors_present

    def _check_config_heading_compatibility(self, configdict, errors_present):
        # Check that listed test_cases coincide with subsection names in Test_Parameters and Model_Parameters, and flag test cases that won't be run
        cases = ['models', 'test_cases']
        params = ['Model Parameters', 'Test Parameters']
        for param, case in zip(params, cases):
            test_cases = configdict['Models and Tests to Run'][case]
            test_parameter_subsections = configdict[param].keys()
            tests_being_run = list()
            if type(test_cases) is list:
                for test_case in test_cases:
                    if test_case not in test_parameter_subsections:
                        logging.info('Error: You have listed test case/model %s, which does not coincide with the corresponding subsection name in the Test Parameters/Model Parameters section. These two names need to be the same, and the keyword must be correct' % test_case)
                        errors_present = bool(True)
                        self._check_for_errors(errors_present=errors_present)
                    else:
                        tests_being_run.append(test_case)
            elif type(test_cases) is str:
                if test_cases not in test_parameter_subsections:
                    logging.info('Error: You have listed test case/model %s, which does not coincide with the corresponding subsection name in the Test Parameters/Model Parameters section. These two names need to be the same, and the keyword must be correct' % test_cases)
                    errors_present = bool(True)
                    self._check_for_errors(errors_present=errors_present)
                else:
                    tests_being_run.append(test_cases)
            for test_case in test_parameter_subsections:
                if test_case not in tests_being_run:
                    logging.info('Note to user: you have specified the test/model %s, which is not listed in your test_cases/models section. MASTML will run fine, but this test will not be performed' % test_case)
        return configdict, errors_present

    def _check_target_feature(self, configdict, errors_present):
        target_feature_name = configdict['General Setup']['target_feature']
        if ('regression' or 'classification') not in target_feature_name:
            logging.info('Error: You must include the designation "regression" or "classification" in your target feature name in your input file and data file. For example: "my_target_feature_regression"')
            errors_present = bool(True)
        return configdict, errors_present

    def _check_for_errors(self, errors_present):
        if errors_present == bool(True):
            logging.info('Errors have been detected in your MASTML setup. Please correct the errors and re-run MASTML')
            sys.exit()
        return

class ModelTestConstructor(object):
    """
    Class that takes parameters from configdict (configfile as dict) and performs calls to appropriate MASTML methods

    Args:
        configfile (MASTML configfile object) : a MASTML input file, as a configfile object

    Methods:
        get_machinelearning_model : obtains machine learning model by calling sklearn

            Args:
                model_type (str) : keyword string indicating sklearn model name
                y_feature (str) : name of target feature

            Returns:
                sklearn model object : an sklearn model object for fitting to data

        get_machinelearning_test : obtains test name to conduct from configdict

            Args:
                test_type (str) : keyword string specifying type of MASTML test to perform
                model (sklearn model object) : sklearn model object to use in test_type
                save_path (str) : path of save directory to store test output

    """
    def __init__(self, configdict):
        self.configdict = configdict

    def get_machinelearning_model(self, model_type, y_feature):
        if 'classification' in y_feature:
            logging.info('Error: Currently, MASTML only supports regression models. Classification models and metrics are under development')
            sys.exit()
            if 'classifier' in model_type:
                logging.info('got y_feature %s' % y_feature)
                logging.info('model type is %s' % model_type)
                logging.info('doing classification on %s' % y_feature)
                if model_type == 'support_vector_machine_model_classifier':
                    model = SVC(C=float(self.configdict['Model Parameters']['support_vector_machine_model_classifier']['error_penalty']),
                                kernel=str(self.configdict['Model Parameters']['support_vector_machine_model_classifier']['kernel']),
                                degree=int(self.configdict['Model Parameters']['support_vector_machine_model_classifier']['degree']),
                                gamma=float(self.configdict['Model Parameters']['support_vector_machine_model_classifier']['gamma']),
                                coef0=float(self.configdict['Model Parameters']['support_vector_machine_model_classifier']['coef0']))
                    return model
                if model_type == 'logistic_regression_model_classifier':
                    model = LogisticRegression(penalty=str(self.configdict['Model Parameters']['logistic_regression_model_classifier']['penalty']),
                                               C=float(self.configdict['Model Parameters']['logistic_regression_model_classifier']['C']),
                                               class_weight=str(self.configdict['Model Parameters']['logistic_regression_model_classifier']['class_weight']))
                    return model
                if model_type == 'decision_tree_model_classifier':
                    model = DecisionTreeClassifier(criterion=str(self.configdict['Model Parameters']['decision_tree_model_classifier']['criterion']),
                                                       splitter=str(self.configdict['Model Parameters']['decision_tree_model_classifier']['splitter']),
                                                       max_depth=int(self.configdict['Model Parameters']['decision_tree_model_classifier']['max_depth']),
                                                       min_samples_leaf=int(self.configdict['Model Parameters']['decision_tree_model_classifier']['min_samples_leaf']),
                                                       min_samples_split=int(self.configdict['Model Parameters']['decision_tree_model_classifier']['min_samples_split']))
                    return model
                if model_type == 'random_forest_model_classifier':
                    model = RandomForestClassifier(criterion=str(self.configdict['Model Parameters']['random_forest_model_classifier']['criterion']),
                                                   n_estimators=int(self.configdict['Model Parameters']['random_forest_model_classifier']['n_estimators']),
                                                   max_depth=int(self.configdict['Model Parameters']['random_forest_model_classifier']['max_depth']),
                                                   min_samples_split=int(self.configdict['Model Parameters']['random_forest_model_classifier']['min_samples_split']),
                                                   min_samples_leaf=int(self.configdict['Model Parameters']['random_forest_model_classifier']['min_samples_leaf']),
                                                   max_leaf_nodes=int(self.configdict['Model Parameters']['random_forest_model_classifier']['max_leaf_nodes']))
                    return model
                if model_type == 'extra_trees_model_classifier':
                    model = ExtraTreesClassifier(criterion=str(self.configdict['Model Parameters']['extra_trees_model_classifier']['criterion']),
                                                 n_estimators=int(self.configdict['Model Parameters']['extra_trees_model_classifier']['n_estimators']),
                                                 max_depth=int(self.configdict['Model Parameters']['extra_trees_model_classifier']['max_depth']),
                                                 min_samples_split=int(self.configdict['Model Parameters']['extra_trees_model_classifier']['min_samples_split']),
                                                 min_samples_leaf=int(self.configdict['Model Parameters']['extra_trees_model_classifier']['min_samples_leaf']),
                                                 max_leaf_nodes=int(self.configdict['Model Parameters']['extra_trees_model_classifier']['max_leaf_nodes']))
                    return model
                if model_type == 'adaboost_model_classifier':
                    model = AdaBoostClassifier(base_estimator= DecisionTreeClassifier(max_depth=int(self.configdict['Model Parameters']['adaboost_model_classifier']['base_estimator_max_depth'])),
                                              n_estimators=int(self.configdict['Model Parameters']['adaboost_model_classifier']['n_estimators']),
                                              learning_rate=float(self.configdict['Model Parameters']['adaboost_model_classifier']['learning_rate']),
                                              random_state=None)
                    return model
                if model_type == 'nn_model_classifier':
                    model = MLPClassifier(hidden_layer_sizes=int(self.configdict['Model Parameters']['nn_model_classifier']['hidden_layer_sizes']),
                                     activation=str(self.configdict['Model Parameters']['nn_model_classifier']['activation']),
                                     solver=str(self.configdict['Model Parameters']['nn_model_classifier']['solver']),
                                     alpha=float(self.configdict['Model Parameters']['nn_model_classifier']['alpha']),
                                     batch_size='auto',
                                     learning_rate='constant',
                                     max_iter=int(self.configdict['Model Parameters']['nn_model_classifier']['max_iterations']),
                                     tol=float(self.configdict['Model Parameters']['nn_model_classifier']['tolerance']))
                    return model

        if 'regression' in y_feature:
            if 'regressor' in model_type:
                logging.info('got y_feature %s' % y_feature)
                logging.info('model type %s' % model_type)
                logging.info('doing regression on %s' % y_feature)
                if model_type == 'linear_model_regressor':
                    model = LinearRegression(fit_intercept=self.configdict['Model Parameters']['linear_model_regressor']['fit_intercept'])
                    return model
                if model_type == 'linear_model_lasso_regressor':
                    model = Lasso(alpha=self.configdict['Model Parameters']['linear_model_lasso_regressor']['alpha'],
                                  fit_intercept=self.configdict['Model Parameters']['linear_model_lasso_regressor']['fit_intercept'])
                    return model
                if model_type == 'support_vector_machine_model_regressor':
                    model = SVR(C=self.configdict['Model Parameters']['support_vector_machine_model_regressor']['error_penalty'],
                                kernel=self.configdict['Model Parameters']['support_vector_machine_model_regressor']['kernel'],
                                degree=self.configdict['Model Parameters']['support_vector_machine_model_regressor']['degree'],
                                gamma=self.configdict['Model Parameters']['support_vector_machine_model_regressor']['gamma'],
                                coef0=self.configdict['Model Parameters']['support_vector_machine_model_regressor']['coef0'])
                    return model
                if model_type == 'lkrr_model_regressor':
                    model = KernelRidge(alpha=self.configdict['Model Parameters']['lkrr_model_regressor']['alpha'],
                                        gamma=self.configdict['Model Parameters']['lkrr_model_regressor']['gamma'],
                                        kernel=self.configdict['Model Parameters']['lkrr_model_regressor']['kernel'])
                    return model
                if model_type == 'gkrr_model_regressor':
                    model = KernelRidge(alpha=self.configdict['Model Parameters']['gkrr_model_regressor']['alpha'],
                                        coef0=self.configdict['Model Parameters']['gkrr_model_regressor']['coef0'],
                                        degree=self.configdict['Model Parameters']['gkrr_model_regressor']['degree'],
                                        gamma=self.configdict['Model Parameters']['gkrr_model_regressor']['gamma'],
                                        kernel=self.configdict['Model Parameters']['gkrr_model_regressor']['kernel'],
                                        kernel_params=None)
                    return model
                if model_type == 'decision_tree_model_regressor':
                    model = DecisionTreeRegressor(criterion=self.configdict['Model Parameters']['decision_tree_model_regressor']['criterion'],
                                                   splitter=self.configdict['Model Parameters']['decision_tree_model_regressor']['splitter'],
                                                   max_depth=self.configdict['Model Parameters']['decision_tree_model_regressor']['max_depth'],
                                                   min_samples_leaf=self.configdict['Model Parameters']['decision_tree_model_regressor']['min_samples_leaf'],
                                                   min_samples_split=self.configdict['Model Parameters']['decision_tree_model_regressor']['min_samples_split'])
                    return model
                if model_type == 'extra_trees_model_regressor':
                    model = ExtraTreesRegressor(criterion=self.configdict['Model Parameters']['extra_trees_model_regressor']['criterion'],
                                                   n_estimators=self.configdict['Model Parameters']['extra_trees_model_regressor']['n_estimators'],
                                                   max_depth=self.configdict['Model Parameters']['extra_trees_model_regressor']['max_depth'],
                                                   min_samples_leaf=self.configdict['Model Parameters']['extra_trees_model_regressor']['min_samples_leaf'],
                                                   min_samples_split=self.configdict['Model Parameters']['extra_trees_model_regressor']['min_samples_split'],
                                                   max_leaf_nodes=self.configdict['Model Parameters']['extra_trees_model_regressor']['max_leaf_nodes'])
                    return model
                if model_type == 'randomforest_model_regressor':
                    model = RandomForestRegressor(criterion=self.configdict['Model Parameters']['randomforest_model_regressor']['criterion'],
                                              n_estimators=self.configdict['Model Parameters']['randomforest_model_regressor']['n_estimators'],
                                              max_depth=self.configdict['Model Parameters']['randomforest_model_regressor']['max_depth'],
                                              min_samples_split=self.configdict['Model Parameters']['randomforest_model_regressor']['min_samples_split'],
                                              min_samples_leaf=self.configdict['Model Parameters']['randomforest_model_regressor']['min_samples_leaf'],
                                              max_leaf_nodes=self.configdict['Model Parameters']['randomforest_model_regressor']['max_leaf_nodes'],
                                              n_jobs=self.configdict['Model Parameters']['randomforest_model_regressor']['n_jobs'],
                                              warm_start=self.configdict['Model Parameters']['randomforest_model_regressor']['warm_start'],
                                              bootstrap=True)
                    return model
                if model_type == 'adaboost_model_regressor':
                    model = AdaBoostRegressor(base_estimator=DecisionTreeRegressor(max_depth=self.configdict['Model Parameters']['adaboost_model_regressor']['base_estimator_max_depth']),
                                              n_estimators=self.configdict['Model Parameters']['adaboost_model_regressor']['n_estimators'],
                                              learning_rate=self.configdict['Model Parameters']['adaboost_model_regressor']['learning_rate'],
                                              loss=self.configdict['Model Parameters']['adaboost_model_regressor']['loss'],
                                              random_state=None)
                    return model
                if model_type == 'nn_model_regressor':
                    model = MLPRegressor(hidden_layer_sizes=self.configdict['Model Parameters']['nn_model_regressor']['hidden_layer_sizes'],
                                     activation=self.configdict['Model Parameters']['nn_model_regressor']['activation'],
                                     solver=self.configdict['Model Parameters']['nn_model_regressor']['solver'],
                                     alpha=self.configdict['Model Parameters']['nn_model_regressor']['alpha'],
                                     batch_size='auto',
                                     learning_rate='constant',
                                     max_iter=self.configdict['Model Parameters']['nn_model_regressor']['max_iterations'],
                                     tol=self.configdict['Model Parameters']['nn_model_regressor']['tolerance'])
                    return model
                if model_type == 'gaussianprocess_model_regressor':
                    test_kernel = None
                    if self.configdict['Model Parameters']['gaussianprocess_model_regressor']['kernel'] == 'rbf':
                        test_kernel = skkernel.ConstantKernel(1.0, (1e-5, 1e5)) * skkernel.RBF(length_scale=self.configdict['Model Parameters']['gaussianprocess_model_regressor']['RBF_length_scale'],
                            length_scale_bounds=tuple(float(i) for i in self.configdict['Model Parameters']['gaussianprocess_model_regressor']['RBF_length_scale_bounds']))
                    model = GaussianProcessRegressor(kernel=test_kernel,
                                                    alpha=self.configdict['Model Parameters']['gaussianprocess_model_regressor']['alpha'],
                                                    optimizer=self.configdict['Model Parameters']['gaussianprocess_model_regressor']['optimizer'],
                                                    n_restarts_optimizer=self.configdict['Model Parameters']['gaussianprocess_model_regressor']['n_restarts_optimizer'],
                                                    normalize_y=self.configdict['Model Parameters']['gaussianprocess_model_regressor']['normalize_y'],
                                                    copy_X_train=True)  # bool(self.configdict['Model Parameters']['gaussianprocess_model']['copy_X_train']),
                                                    # int(self.configdict['Model Parameters']['gaussianprocess_model']['random_state']
                    return model
                else:
                    model = None
                    return model

        elif model_type == 'custom_model':
            model_dict = self.configdict['Model Parameters']['custom_model']
            package_name = model_dict.pop('package_name') #return and remove
            class_name = model_dict.pop('class_name') #return and remove
            import importlib
            custom_module = importlib.import_module(package_name)
            module_class_def = getattr(custom_module, class_name) 
            model = module_class_def(**model_dict) #pass all the rest as kwargs
            return model
        elif model_type == 'load_model':
            model_dict = self.configdict['Model Parameters']['load_model']
            model_location = model_dict['location'] #pickle location
            from sklearn.externals import joblib
            model = joblib.load(model_location)
            return model
        #else:
        #    raise TypeError('You have specified an invalid model_type name in your input file')

    def get_machinelearning_test(self, test_type, model, save_path, run_test=True, *args, **kwargs):
        mod_name = test_type.split("_")[0] #ex. KFoldCV_5fold goes to KFoldCV
        test_module = importlib.import_module('%s' % (mod_name))
        test_class_def = getattr(test_module, mod_name)
        logging.debug("Parameters passed by keyword:")
        logging.debug(kwargs)
        test_class = test_class_def(model=model,
                            save_path = save_path,
                            **kwargs)
        if run_test == True:
            test_class.run()
        return test_class

    def _process_config_keyword(self, keyword):
        keywordsetup = {}
        if not self.configdict[str(keyword)]:
            raise IOError('This dict does not contain the relevant key, %s' % str(keyword))
        for k, v in self.configdict[str(keyword)].items():
            keywordsetup[k] = v
        return keywordsetup