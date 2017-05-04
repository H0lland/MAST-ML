import matplotlib.pyplot as plt
import matplotlib
import data_parser
import numpy as np
import os
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics import mean_squared_error
import data_analysis.printout_tools as ptools
import portion_data.get_test_train_data as gttd
from SingleFit import timeit
from SingleFitGrouped import SingleFitGrouped
import plot_data.plot_xy as plotxy
import plot_data.plot_from_dict as plotdict
import copy
import time

class PredictionVsFeature(SingleFitGrouped):
    """Make prediction vs. feature plots from a single fit.
        training_dataset,
        testing_dataset, (Multiple testing datasets are allowed as a list.)
        model,
        save_path,
        input_features,
        target_feature,
        target_error_feature,
        labeling_features,
        xlabel,
        ylabel,
        stepsize,
        plot_filter_out,
        grouping_feature,
        fit_only_on_matched_groups,
        mark_outlying_groups, see parent class.
        feature_plot_xlabel <str>: x-axis label for per-group plots of predicted and
                                measured y data versus data from field of
                                numeric_field_name
        feature_plot_ylabel <str>: y-axis label for per-group plots
        feature_plot_feature <str>: feature for per-group feature plots
        markers <str>: comma-delimited marker list for split plots
        outlines <str>: comma-delimited color list for split plots
        linestyles <str>: comma-delimited list of line styles for split plots
        data_labels <str>: comma-delimited list of labels for split plots; order
                        should be Train, Test, Test, Test... with testing
                        data in order of test_csv
    """
    def __init__(self, 
        training_dataset=None,
        testing_dataset=None,
        model=None,
        save_path=None,
        input_features=None,
        target_feature=None,
        target_error_feature=None,
        labeling_features=None,
        xlabel="Measured",
        ylabel="Predicted",
        stepsize=1,
        plot_filter_out = "",
        grouping_feature = None,
        mark_outlying_groups = 2,
        fit_only_on_matched_groups = 0,
        feature_plot_xlabel = "X",
        feature_plot_ylabel = "Prediction",
        feature_plot_feature = "",
        markers="",
        outlines="",
        data_labels="",
        linestyles="",
        *args, **kwargs):
        """
            Additional class attributes not in parent class:
           
            Set by keyword:
            self.testing_datasets <list of data objects>: testing datasets
            self.feature_plot_xlabel <str>: x-axis label for feature plots
            self.feature_plot_ylabel <str>: y-axis label for feature plots
            self.feature_plot_feature <str>: feature for feature plots
            self.markers <list of str>: list of markers for plotting
            self.outlines <list of str>: list of edge colors for plotting
            self.linestyles <list of str>: list of linestyles for plotting
            self.data_labels <list of str>: list of data labels for plotting
            
            Set by code:
            self.testing_dataset_dict <dict of data objects>: testing datasets
            self.sfg_dict <dict of SingleFitGrouped objects>
        """
        SingleFitGrouped.__init__(self, 
            training_dataset=training_dataset, 
            testing_dataset=testing_dataset,
            model=model, 
            save_path = save_path,
            input_features = input_features, 
            target_feature = target_feature,
            target_error_feature = target_error_feature,
            labeling_features = labeling_features,
            xlabel=xlabel,
            ylabel=ylabel,
            stepsize=stepsize,
            plot_filter_out = plot_filter_out,
            grouping_feature = grouping_feature,
            mark_outlying_groups = mark_outlying_groups,
            fit_only_on_matched_groups = fit_only_on_matched_groups)
        #Sets by keyword
        self.testing_datasets = testing_dataset #expect a list of one or more testing datasets
        self.feature_plot_xlabel = feature_plot_xlabel
        self.feature_plot_ylabel = feature_plot_ylabel
        self.feature_plot_feature = feature_plot_feature
        self.markers = markers
        self.outlines = outlines
        self.data_labels = data_labels
        self.linestyles = linestyles
        #Sets in code
        self.testing_dataset_dict = dict() 
        self.sfg_dict=dict()
        return
   
    @timeit
    def run(self):
        self.set_up()
        self.get_sfg_dict()
        self.plot()
        self.print_readme()
        return

    @timeit
    def set_up(self):
        self.readme_list.append("%s\n" % time.asctime())
        tidxs = np.arange(0, len(self.testing_datasets)) 
        for tidx in tidxs:
            test_data_label = self.data_labels[tidx+1] #first one is training
            self.testing_dataset_dict[test_data_label] = copy.deepcopy(self.testing_datasets[tidx])
        return

    @timeit
    def get_sfg_dict(self):
        """Get SingleFitGrouped dictionary.
        
            Each entry will be a SingleFitGrouped object,
            one for each of the testing datasets.
        """
        self.readme_list.append("----- Fitting and prediction -----\n")
        self.readme_list.append("See results per dataset in subfolders\n")
        for testset in self.testing_dataset_dict.keys():
            self.sfg_dict[testset] = SingleFitGrouped( 
                training_dataset = self.training_dataset, 
                testing_dataset = self.testing_dataset_dict[testset],
                model = self.model, 
                save_path = os.path.join(self.save_path, str(testset)),
                input_features = self.input_features, 
                target_feature = self.target_feature,
                target_error_feature = self.target_error_feature,
                labeling_features = self.labeling_features,
                xlabel=self.xlabel,
                ylabel=self.ylabel,
                stepsize=self.stepsize,
                plot_filter_out = self.plot_filter_out,
                grouping_feature = self.grouping_feature,
                mark_outlying_groups = self.mark_outlying_groups,
                fit_only_on_matched_groups = self.fit_only_on_matched_groups)
            self.sfg_dict[testset].run()
            self.readme_list.append("  %s" % testset)
        return

    @timeit
    def plot(self):
        return

    @timeit
    def make_overall_plot(self, plabel="unfiltered_overall", use_filters=False):
        """Make overall plot of predicted vs. measured"""
        edict=dict() #here 'groups' will be data series. 
        group_notelist = list()
        if use_filters:
            group_notelist.append("Data not displayed:")
            for pfstr in self.plot_filter_out:
                group_notelist.append(pfstr.replace(";"," "))
            group_notelist.append("RMSEs for displayed data:")
        else:
            group_notelist.append("RMSEs:")
        for label in self.extrapolation_dict.keys():
            if not('rmse' in self.extrapolation_dict[label].overall_analysis.statistics.keys()):
                continue #no measured data; cannot be plotted
            s_analysis = self.extrapolation_dict[label].overall_analysis
            if use_filters:
                use_index = self.plot_filter_dict[label]['nogroup']
            else:
                use_index = np.arange(0, len(s_analysis.testing_target_prediction))
            edict[label] = dict()
            edict[label]['xdata'] = s_analysis.testing_target_data[use_index]
            if self.target_error_feature is None:
                edict[label]['xerrdata'] = np.zeros(len(use_index))
            else:
                edict[label]['xerrdata'] = s_analysis.testing_target_data_error[use_index]
            edict[label]['ydata'] = s_analysis.testing_target_prediction[use_index]
            edict[label]['rmse'] = np.sqrt(mean_squared_error(edict[label]['ydata'],edict[label]['xdata']))
        series_list = list(edict.keys())
        if len(series_list) == 0:
            logging.info("No series for overall plot in extrapolatefullfit.")
            return
        addl_kwargs=dict()
        addl_kwargs['save_path'] = os.path.join(self.save_path, plabel)
        plotdict.plot_group_splits_with_outliers(group_dict=edict,
            outlying_groups = series_list,
            label=plabel,
            group_notelist = list(group_notelist),
            addl_kwargs = dict(addl_kwargs))
        return
    
    @timeit
    def make_plotting_filter_index(self, dataset, preexisting_index=None):
        plot_index = list()
        out_index = list()
        for pfstr in self.plot_filter_out:
            pflist = pfstr.split(";")
            feature = pflist[0].strip()
            symbol = pflist[1].strip()
            rawvalue = pflist[2].strip()
            try:
                value = float(rawvalue)
            except ValueError:
                value = rawvalue
            featuredata = np.asarray(dataset.get_data(feature)).ravel()
            for fidx in range(0, len(featuredata)):
                fdata = featuredata[fidx]
                if fdata is None:
                    continue
                if symbol == "<":
                    if fdata < value:
                        out_index.append(fidx)
                elif symbol == ">":
                    if fdata > value:
                        out_index.append(fidx)
                elif symbol == "=":
                    if fdata == value:
                        out_index.append(fidx)
        if preexisting_index is None:
            preexisting_index = np.arange(0, len(np.asarray(dataset.get_data(feature)).ravel()))
        out_index = np.unique(out_index)
        plot_index = np.setdiff1d(preexisting_index, out_index)
        return plot_index

    @timeit
    def make_plotting_filter_dict(self):
        """Needs rework with dataframes
        """
        pdict=dict()
        for label in self.extrapolation_dict.keys():
            pdict[label]=dict()
            pdict[label]['nogroup'] = self.make_plotting_filter_index(self.extrapolation_dict[label].testing_dataset)
            if self.group_field_name is None:
                pass
            else:
                for group in self.extrapolation_dict[label].test_groups:
                    pdict[label][group] = self.make_plotting_filter_index(self.extrapolation_dict[label].testing_dataset, self.extrapolation_dict[label].test_group_indices[group]['test_index'])
        #for training data, all have same training data; use last label
        tlabel = self.data_labels[0]
        pdict[tlabel]=dict()
        pdict[tlabel]['nogroup'] = self.make_plotting_filter_index(self.training_dataset[0])
        if self.group_field_name is None:
            pass
        else:
            for group in self.extrapolation_dict[label].train_groups:
                pdict[tlabel][group] = self.make_plotting_filter_index(self.training_dataset[0], self.extrapolation_dict[label].train_group_indices[group]['test_index'])
        self.plot_filter_dict = dict(pdict)
        return

    @timeit
    def make_series_feature_plot(self, plabel="feature_plots", use_filters=False, show_training=True, group=None):
        """Make series feature plot
        """
        edict=dict() #here 'groups' will be data series. 
        group_notelist = list()
        if use_filters:
            group_notelist.append("Data not displayed:")
            for pfstr in self.plot_filter_out:
                group_notelist.append(pfstr.replace(";"," "))
        if show_training:
            label = self.data_labels[0] #training label
            edict[label] = dict()
            if use_filters:
                if group is None:
                    use_index = self.plot_filter_dict[label]['nogroup']
                else:
                    use_index = self.plot_filter_dict[label][group]
            else:
                use_index = np.arange(0, len(np.asarray(self.training_dataset[0].get_data(self.target_feature)).ravel()))
            edict[label]['xdata'] = np.asarray(self.training_dataset[0].get_data(self.feature_plot_field)).ravel()[use_index]
            edict[label]['xerrdata'] = None
            edict[label]['ydata'] = np.asarray(self.training_dataset[0].get_data(self.target_feature)).ravel()[use_index]
        for label in self.extrapolation_dict.keys():
            s_analysis = self.extrapolation_dict[label].overall_analysis
            if use_filters:
                if group is None:
                    use_index = self.plot_filter_dict[label]['nogroup']
                else:
                    use_index = self.plot_filter_dict[label][group]
            else:
                use_index = np.arange(0, s_analysis.testing_input_data.shape[0])
            if not(s_analysis.testing_target_data is None):
                mlabel = "%s measured" % label
                edict[mlabel] = dict()
                edict[mlabel]['xdata'] = np.asarray(s_analysis.testing_dataset.get_data(self.feature_plot_field)).ravel()[use_index]
                edict[mlabel]['xerrdata'] = None
                edict[mlabel]['ydata'] = s_analysis.testing_target_data[use_index]
            slabel = "%s predicted" % label
            edict[slabel] = dict()
            edict[slabel]['xdata'] = np.asarray(s_analysis.testing_dataset.get_data(self.feature_plot_field)).ravel()[use_index]
            edict[slabel]['xerrdata'] = None
            edict[slabel]['ydata'] = s_analysis.testing_target_prediction[use_index]
        series_list = list(edict.keys())
        if len(series_list) == 0:
            logging.info("No series for plot.")
            return
        addl_kwargs=dict()
        addl_kwargs['guideline'] = 0
        addl_kwargs['save_path'] = os.path.join(self.save_path, plabel)
        addl_kwargs['xlabel'] = self.feature_plot_xlabel
        addl_kwargs['ylabel'] = self.feature_plot_ylabel
        addl_kwargs['markers'] = self.markers
        addl_kwargs['outlines'] = self.outlines
        addl_kwargs['linestyles'] = self.linestyles
        faces = list()
        for fidx in range(0, len(self.markers)):
            faces.append("None")
        addl_kwargs['faces'] = faces
        plotdict.plot_group_splits_with_outliers(group_dict=edict,
            outlying_groups = series_list,
            label=plabel,
            group_notelist = list(group_notelist),
            addl_kwargs = dict(addl_kwargs))
        return

    @timeit
    def oldrun(self):
        self.get_extrapolation_dict()
        self.make_overall_plot("overall_plot_unfiltered",use_filters=False)
        if not(self.plot_filter_out is None):
            self.make_plotting_filter_dict()
            self.make_overall_plot("overall_plot_filtered",use_filters=True)
        for group in self.plot_filter_dict[self.data_labels[0]].keys():
            self.make_series_feature_plot("series_feature_plot_unfiltered_%s" % group,use_filters=False, 
                    show_training=True, group=group)
            self.make_series_feature_plot("series_feature_plot_filtered_%s" % group,use_filters=True, 
                    show_training=True, group=group)
        return


def execute(model, data, savepath, 
        test_csvs = None,
        group_field_name = None,
        label_field_name = None,
        numeric_field_name = None,
        xlabel="Measured",
        ylabel="Predicted",
        split_xlabel = "X",
        split_ylabel = "Prediction",
        stepsize=1,
        markers="",
        outlines="",
        labels="",
        linestyles="",
        measured_error_field_name = None,
        plot_filter_out = "",
        fit_only_on_matched_groups = 0,
        *args,**kwargs):
    """Do full fit for extrapolation.
        test_csvs <str>: comma-delimited list of test csv name
        group_field_name <str>: field name for grouping data
        label_field_name <str>: field name for labels corresponding to groups
        numeric_field_name <str>: field name for numeric data that will be used
                                    on the x-axis in per-group plots
        xlabel <str>: x-axis label for predicted-vs-measured plot
        ylabel <str>: y-axis label for predicted-vs-measured plot
        stepsize <float>: step size for predicted-vs-measured plot grid
        split_xlabel <str>: x-axis label for per-group plots of predicted and
                                measured y data versus data from field of
                                numeric_field_name
        split_ylabel <str>: y-axis label for per-group plots
        measured_error_field_name <str>: field name for measured y-data error (optional)
        plot_filter_out <str>: semicolon-delimited filters for plotting,
                                each a comma-delimited triplet, for example,
                                temperature,<,3000
                                See data_parser
        fit_only_on_matched_groups <int>: 1 - fit only on groups that exist
                                            in both the training data and
                                            the test_csv data
                                          0 - fit on all data in the training
                                                dataset (default)
                                        Only works if group_field_name is set.
        markers <str>: comma-delimited marker list for split plots
        outlines <str>: comma-delimited color list for split plots
        linestyles <str>: comma-delimited list of line styles for split plots
        labels <str>: comma-delimited list of labels for split plots; order
                        should be Train, Test, Test, Test... with testing
                        data in order of test_csv
    """
    stepsize=float(stepsize)
    #get datasets
    ##training
    if numeric_field_name == None: #help identify each point
        numeric_field_name = data.x_features[0]
    if not(group_field_name is None):
        if label_field_name is None:
            label_field_name = group_field_name
    ##testing
    lsplit = labels.split(",")
    data_labels = list()
    test_labels = list()
    for litem in lsplit:
        data_labels.append(litem.strip())
    test_labels = list(data_labels[1:]) #not the training label
    if test_csvs == None:
        raise ValueError("test_csvs is None")
    test_csv_list = list()
    tcsplit = test_csvs.split(",")
    for tcitem in tcsplit:
        test_csv_list.append(tcitem.strip())
    test_sets = dict()
    for tidx in range(0,len(test_labels)):
        test_csv = test_csv_list[tidx]
        test_label = test_labels[tidx]
        test_sets[test_label]=dict()
        unfiltered_test_data = data_parser.parse(test_csv)
        test_sets[test_label]['test_data_unfiltered'] = unfiltered_test_data
        test_data = data_parser.parse(test_csv)
        if len(plot_filter_out) > 0:
            ftriplets = plot_filter_out.split(";")
            for ftriplet in ftriplets:
                fpcs = ftriplet.split(",")
                ffield = fpcs[0].strip()
                foperator = fpcs[1].strip()
                fval = fpcs[2].strip()
                try:
                    fval = float(fval)
                except (ValueError, TypeError):
                    pass
                test_data.add_exclusive_filter(ffield, foperator, fval)
        hasy = test_data.set_y_feature(data.y_feature) # same feature as fitting data
        if hasy is False:
            test_data.set_y_feature(data.x_features[0]) # dummy y feature
            test_sets[test_label]['dummy_ydata'] = True
        test_sets[test_label]['test_ydata'] = np.asarray(test_data.get_y_data()).ravel()
        test_data.set_x_features(data.x_features) #same features as fitting data
        test_sets[test_label]['test_data']=test_data
        test_sets[test_label]['test_xdata'] = np.asarray(test_data.get_x_data())
        test_sets[test_label]['test_numericdata'] = np.asarray(test_data.get_data(numeric_field_name)).ravel()
        if not(group_field_name is None):
            test_sets[test_label]['test_groupdata'] = np.asarray(test_data.get_data(group_field_name)).ravel()
            test_sets[test_label]['test_labeldata'] = np.asarray(test_data.get_data(label_field_name)).ravel()
        else:
            test_sets[test_label]['test_groupdata'] = None
            test_sets[test_label]['test_labeldata'] = None
        if not(measured_error_field_name == None):
            test_sets[test_label]['test_yerrdata'] = np.asarray(test_data.get_data(measured_error_field_name)).ravel()
        else:
            test_sets[test_label]['test_yerrdata'] = None
    # filter out for only matched groups
    if int(fit_only_on_matched_groups) == 1:
        if group_field_name == None:
            pass
        else:
            train_groupdata = np.asarray(data.get_data(group_field_name)).ravel()
            train_indices = gttd.get_logo_indices(train_groupdata)
            for test_label in test_labels:
                test_groupdata = test_sets[test_label]['test_groupdata']
                groups_not_in_test = np.setdiff1d(train_groupdata, test_groupdata)
                for outgroup in groups_not_in_test:
                    data.add_exclusive_filter(group_field_name,"=",outgroup)
                train_xdata = np.asarray(data.get_x_data())
                test_sets[test_label]['train_xdata'] = train_xdata
                train_ydata = np.asarray(data.get_y_data()).ravel()
                test_sets[test_label]['train_ydata'] = train_ydata
                train_groupdata = np.asarray(data.get_data(group_field_name)).ravel()
                test_sets[test_label]['train_groupdata'] = train_groupdata
                data.remove_all_filters()
    else:
        if group_field_name is None:
            pass
        else:
            train_groupdata = np.asarray(data.get_data(group_field_name)).ravel()
            train_xdata = np.asarray(data.get_x_data())
            train_ydata = np.asarray(data.get_y_data()).ravel()
            for test_label in test_labels:
                test_sets[test_label]['train_xdata'] = train_xdata
                test_sets[test_label]['train_ydata'] = train_ydata
                test_sets[test_label]['train_groupdata'] = train_groupdata
    #
    if len(plot_filter_out) > 0:
        ftriplets = plot_filter_out.split(";")
        for ftriplet in ftriplets:
            fpcs = ftriplet.split(",")
            ffield = fpcs[0].strip()
            foperator = fpcs[1].strip()
            fval = fpcs[2].strip()
            try:
                fval = float(fval)
            except (ValueError, TypeError):
                pass
            data.add_exclusive_filter(ffield, foperator, fval)
    train_xdata_toplot = np.asarray(data.get_x_data())
    train_ydata_toplot = np.asarray(data.get_y_data()).ravel()
    train_numericdata_toplot = np.asarray(data.get_data(numeric_field_name)).ravel()
    if not(group_field_name is None):
        train_groupdata_toplot = np.asarray(data.get_data(group_field_name)).ravel()
    else:
        train_groupdata_toplot = None
    #
    for test_label in test_labels:
        kwargs_f = dict()
        kwargs_f['xlabel'] = xlabel
        kwargs_f['ylabel'] = ylabel
        kwargs_f['stepsize'] = stepsize
        kwargs_f['numeric_field_name'] = numeric_field_name
        kwargs_f['group_field_name'] = group_field_name
        kwargs_f['savepath'] =os.path.join(savepath,test_label.replace(" ","_"))
        if not (os.path.isdir(kwargs_f['savepath'])):
            os.mkdir(kwargs_f['savepath'])
        kwargs_f['do_pergroup_fits'] = 0 # NO per-group fitting
        kwargs_f['test_numericdata'] = test_sets[test_label]['test_numericdata']
        if not(group_field_name == None):
            kwargs_f['test_groupdata'] = test_sets[test_label]['test_groupdata']
            kwargs_f['train_groupdata'] = test_sets[test_label]['train_groupdata']
            kwargs_f['label_field_name'] = label_field_name
            kwargs_f['test_labeldata'] = test_sets[test_label]['test_labeldata']
        if not(measured_error_field_name == None):
            kwargs_f['test_yerrdata'] = test_sets[test_label]['test_yerrdata']
        kwargs_f['full_xtrain'] = test_sets[test_label]['train_xdata']
        kwargs_f['full_ytrain'] = test_sets[test_label]['train_ydata']
        kwargs_f['full_xtest'] = test_sets[test_label]['test_xdata']
        kwargs_f['full_ytest'] = test_sets[test_label]['test_ydata']
        test_data_array = FullFit.do_full_fit(model, **kwargs_f)
        test_sets[test_label]['fullfit_results_array'] = test_data_array
    
    if numeric_field_name is None: #no numeric plots to do
        return
    #return #TTM DEBUG
    if group_field_name == None:
        numericidx=0
        groupidx = -1
        labelidx = -1
        measuredidx = 1
        predictedidx = 2
    else:
        numericidx=0 #numeric
        groupidx = 1 #group
        labelidx = 2 #label
        measuredidx = 3 #measured
        predictedidx = 4 #predicted
    #set results
    for test_label in test_labels:
        if 'dummy_ydata' in test_sets[test_label].keys(): #dummy y data was needed for full fit, but is no longer needed
            test_sets[test_label]['test_ydata'] = None 
        test_sets[test_label]['test_predicted'] = np.array(test_sets[test_label]['fullfit_results_array'][:,predictedidx])
    do_numeric_plots(train_x = train_numericdata_toplot,
                    train_y = train_ydata_toplot,
                    train_groupdata = train_groupdata_toplot,
                    data_labels = list(data_labels),
                    test_sets = dict(test_sets),
                    markers=markers,
                    outlines = outlines,
                    linestyles = linestyles,
                    xlabel = split_xlabel,
                    ylabel = split_ylabel,
                    plotlabel="alldata",
                    savepath = savepath,
                    group_index = None)
    if group_field_name is None: #no individual numeric plots by group necessary
        return
    groups = np.unique(train_groupdata)
    for test_label in test_labels:
        groups = np.concatenate((groups, np.unique(test_sets[test_label]['test_groupdata'])))
    groups = np.unique(groups)
    for group in groups:
        do_numeric_plots(train_x = train_numericdata_toplot,
                    train_y = train_ydata_toplot,
                    train_groupdata = train_groupdata_toplot,
                    data_labels = list(data_labels),
                    test_sets = dict(test_sets),
                    markers=markers,
                    outlines = outlines,
                    linestyles = linestyles,
                    xlabel = split_xlabel,
                    ylabel = split_ylabel,
                    plotlabel="%s" % group,
                    savepath = savepath,
                    group_index = group)
    return

def do_numeric_plots(train_x="",train_y="",
            train_groupdata=None,
            data_labels="",
            test_sets="", 
            markers="", outlines="", linestyles="", 
            xlabel="X",
            ylabel="Y",
            plotlabel="",
            savepath="", group_index=None):
    #plot all results together by numericdata
    markerlist = markers.split(",")
    outlinelist = outlines.split(",")
    linestylelist = linestyles.split(",")
    xdatalist=list()
    ydatalist=list()
    xerrlist=list()
    yerrlist=list()
    labellist=list()
    markerstr=""
    linestylestr=""
    outlinestr=""
    facestr=""
    sizestr=""
    linect = 0
    if group_index is None:
        train_index = range(0, len(train_x))
    else:
        train_indices = gttd.get_logo_indices(train_groupdata)
        if group_index in train_indices.keys():
            train_index = train_indices[group_index]['test_index']
        else:
            train_index = list()
    if len(train_index) > 0:
        train_x_g = train_x[train_index]
        train_y_g = train_y[train_index]
        xdatalist.append(train_x_g)
        ydatalist.append(train_y_g)
        xerrlist.append(None)
        yerrlist.append(None)
        labellist.append(data_labels[0])
        markerstr = markerlist[0] + ","
        linestylestr = linestylelist[0] + ","
        outlinestr = outlinelist[0] + ","
        facestr="None,"
        sizestr="10,"
    for test_label in data_labels[1:]:
        mytest = dict(test_sets[test_label])
        if group_index is None:
            test_index = range(0, len(mytest['test_predicted']))
        else:
            test_indices = gttd.get_logo_indices(mytest['test_groupdata'])
            if group_index in test_indices.keys():
                test_index = test_indices[group_index]['test_index']
            else:
                test_index = list()
        if len(test_index) > 0:
            if not (mytest['test_ydata'] is None):
                linect = linect + 1
                xdatalist.append(mytest['test_numericdata'][test_index])
                ydatalist.append(mytest['test_ydata'][test_index])
                xerrlist.append(None)
                yerrlist.append(None)
                labellist.append("%s, measured" % test_label)
                markerstr = markerstr + markerlist[linect] + ","
                outlinestr = outlinestr + outlinelist[linect] + ","
                linestylestr = linestylestr + linestylelist[linect] + ","
                sizestr = sizestr+ "10,"
                facestr = facestr+ "None,"
            linect = linect + 1
            xdatalist.append(mytest['test_numericdata'][test_index])
            ydatalist.append(mytest['test_predicted'][test_index])
            xerrlist.append(None)
            yerrlist.append(None)
            labellist.append("%s, predicted" % test_label)
            markerstr = markerstr + markerlist[linect] + ","
            outlinestr = outlinestr + outlinelist[linect] + ","
            linestylestr = linestylestr + linestylelist[linect] + ","
            sizestr = sizestr+ "10,"
            facestr = facestr+ "None,"
    kwargs_p = dict()
    kwargs_p['savepath'] = os.path.join(savepath,"%s" % plotlabel)
    if not os.path.isdir(kwargs_p['savepath']):
        os.mkdir(kwargs_p['savepath'])
    kwargs_p['xlabel'] = xlabel
    kwargs_p['ylabel'] = ylabel
    kwargs_p['guideline'] = 0
    kwargs_p['linestyles'] = linestylestr[:-1] #remove trailing comma
    kwargs_p['markers'] = markerstr[:-1]
    kwargs_p['outlines'] = outlinestr[:-1]
    kwargs_p['sizes'] = sizestr[:-1]
    kwargs_p['faces'] = facestr[:-1]
    kwargs_p['xdatalist'] = xdatalist
    kwargs_p['ydatalist'] = ydatalist
    kwargs_p['xerrlist'] = xerrlist
    kwargs_p['yerrlist'] = yerrlist
    kwargs_p['labellist'] = labellist
    kwargs_p['plotlabel'] = plotlabel
    plotxy.multiple_overlay(**kwargs_p)
    return
