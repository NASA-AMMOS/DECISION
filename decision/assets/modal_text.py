from dash            import html

GENETIC_ALGORITHM_CONFIGURATION = [
    html.Div("DECISION uses a Genetic Algorithm to converge on the desired optimal metrics."),
    html.Br(),
    html.Div("Genetic Algorithms (GA) use biologically inspired operators such as mutation, crossover, and selection to arrive \
             at optimal solutions to problems. Generally, GA's use an iterative process to explore a solution space, and then \
             exploit what it learns to optimize for the selected metrics."),
    html.Br(),
    html.Div("Beginning with a random population of variables, where the range of the variables is defined by the \
             Parameter Optimization section on the Metrics page, the GA will evaluate the fitness of each individual \
             in the population at solving the problem, where fitness is derived from the selected Optimization Metrics \
             on the Metrics page. \
             The highest fitness individuals will be selected and modified, using the variables below, within the bounds defined \
             in the Parameter Optimization page to create the next generation (iteration). Thus, optimization occurs by continuously \
             selecting the value of variables that produce the best results in an iteration, and slightly modifying those variables \
             in an attempt to achieve a better result in the next iteration. \
             This process begins by selecting the Run button and will continue until the Maximum Iterations is reached, or until \
             stopped by selecting the Stop button."),
    html.Br(),
    html.Div("There are a number of parameters below that modify how the Genetic Algorithm converges on an optimal solution. \
             You may adjust these parameters below.")
]
PARAMETER_OPTIMIZATION = [
    html.Div("Parameter Optimization is used to identify the optimial settings \
                for a particular problem that the learning algorithm is trying to solve."),
    html.Br(),
    html.Div("There are generally two types of settings available: variables, and constants. \
                Variables are settings that the learning algorithm will optimize for. \
                Constants are settings that will remain unchanged during the optimization process. \
                If applicable, constants will be denoted by a `Constants` title and by having `Constant` \
                on either side of the slider."),
    html.Br(),
    html.Div("Below, you may select the range of variables and/or constants for the \
                learning algorithm to explore, depending upon the selected project's configuration."),
    html.Br(),
    html.Div("For each parameter, the larger the range of potential values that the algorithm is \
                optimizing for, the longer the parameter optimization will take. Thus, decreasing \
                the range of values below will reduce the overall runtime estimate seen on the right."),
    html.Br(),
    html.Div("When selecting the range of settings, consider the context of the problem. For example, \
                if there is a high risk associated with making the wrong decision, you may consider \
                having the range of parameters to explore be large. This will ensure that the learning algorithm \
                does not find a local optimization, and rather explores the entire feature space for a global optimization. \
                However, this will also ensure that the learning algorithm takes a longer time to optimize. If the \
                problem requires quick decision making, and the risk associated with making a decision too slowly \
                is larger than the risk associated with making the best decision, then it may be worthwhile to \
                decrease the range of parameters to decrease the learning time, thus reducing risk. In \
                many instances, it is likely that the problem will require a balance between parameter space \
                and time. The greater the understanding you have of the problem will allow you to better \
                find this balance."),
]
METRICS_TO_OPTIMIZE = [
    html.Div("The purpose of the DECISION application is to train learning algorithms on a set of data to \
              optimize metrics that will reduce risk and increase scientific return."),
    html.Br(),
    html.Div("The optimization metrics that are selected below should be based on the constraints of the given application. \
             At least two metrics must be selected to optimize."),
    html.Br(),
    html.Div("For example, for a mission where the most significant constraint is bandwidth, it may be worthwhile to \
             minimize data volume and maximize precision in order to limit the overall amount of data to downlink, and ensure \
             that the samples that you are downloading are valuable. \
             On the other hand, for a mission where there is only one opportunity for data collection but minimal resource \
             constraints for downlink, optimizing to maximize recall and minimize run time could more impactfully reduce risk \
             by aiming to collect as many positive samples as possible, even if it includes various false positive samples."),
    html.Br(),
    html.Div("Recall, also known as sensitivity, is the proportion of true positive cases that were identified as positive examples \
             by the learning algorithm. Maximizing recall will ensure that as many true positive cases as possible are identified, even \
             if it also results in a higher number of false positives."),
    html.Br(),
    html.Div("Precision, also known as the positive predictive value, measures the proportion of true positive cases among both true \
             and false positive preditions. Maxmimizing precision will increase the likelihood of true positive \
             predictions, thereby minimizing the number of false positives."),
    html.Br(),
    html.Div("False Positives are false predictions made by the classifier suggesting that the sample contains the sought \
             after class, when it in fact does not. Minimizing false positives will reduce the number of false predictions."),
    html.Br(),
    html.Div("F1 Score is the harmonic mean of the precision and recall, weighting both precision and recall equally. \
             Maximizing the F1 Score will result in both high precision and recall."),
    html.Br(),
    html.Div("Runtime is the time it takes to complete a task or process. Minimizing runtime will result in a faster prediction \
             algorithm."),
    html.Br(),
    html.Div("Data Volume, measured in bytes, is the amount of data being processed or stored. \
             Minimizing Data Volume will produce results that take up smaller amounts of digital storage and improve processing efficiency."),
    html.Br(),
    html.Div("OSIA RAM, Onboard Science Instrument Autonomy Random Access Memory, is referring to the required amount of short term memory \
             the OSIA application requires to operate. Minimizing OSIA RAM will result in prediction algorithms that require less \
             RAM and may improve processing efficiency."),
]
EXPERIMENTS_TO_OPTIMIZE_WITH = [
    html.Div("Learning algorithms use training data in order to develop a model of the problem it is trying to solve. \
             Thus, the data that a learning algorithm is trained on will have a significant impact on the algorithm's \
             ability to solve a particular problem."),
    html.Br(),
    html.Div("Below, you must select at least one dataset (experiment) for the learning algorithm to optimize on. \
             More than one dataset may be selected."),
    html.Br(),
    html.Div("When selecting datasets, you should consider their size and contents. Selected datasets should have \
             very similar features compared to what you are looking for. The larger number of examples you have in your dataset, \
             the more robust the resulting parameters will be."),
    html.Br(),
    html.Div("For example, if your intent is to determine the optimal parameters for an instrument to discover \
             dried river beds on Mars, utilizing a dataset that has similar features to the area of interest, such as sandy terrain, \
             would produce better results than a dataset that has very different features to the area of interest, \
             such as mountainous terrain."),
    html.Br(),
    html.Div("Optionally, you may select or deselect all the listed experiments by utilizing the buttons below. You may \
             sort the datasets by selecting the arrows next to each column header to sort in ascending or descending order \
             for the respective column. Finally, you may filter data by selecting and typing the sought after feature in the row \
             below the header of the respective column."),
]
CONFIGURATION_DATABASE = [
    html.Div("The Configuration Database is a table that shows each of the metrics defined on the Metrics page, inclusive \
             of the selected Optimization Metrics, and the parameters used to arrive at the Optimization Metrics. \
             Each row denotes a specific configuration."),
    html.Br(),
    html.Div("The Configuration Database is used to select configurations to be tested on the Test page, and to \
             see the numerical relationships between the variables."),
    html.Br(),
    html.Div("Select configurations to be tested on the Test Page by selecting the checkbox on the left. Alternatively, \
             configurations may be selected using the Box Select Tool or the Lasso Select tool in the Configuration Search Space."),
    html.Br(),
    html.Div("To find specific configurations, you may optionally use either the second row in the table to filter results, \
             denoted 'filter data...', or select the arrows next to each column name to sort in either ascending or descending order."),
    html.Br(),
    html.Div("The table contains many columns, and may require that you scroll using the scroll bar on the bottom to see all of the results.")
]
CONFIGURATION_SEARCH_SPACE = [
    html.Div("The Configuration Search Space is shown using a scatter plot. The Configuration Search Space can be \
             used to graphically find the configurations that provide optimal results across the selected metrics."),
    html.Br(),
    html.Div("Each of the axes of the scatter plot are set to be one of the metrics defined on the Metrics Page. \
             The axes for the scatter plot may be modified by using the dropdown menu next to the corresponding axis."),
    html.Br(),
    html.Div("There are a number of tools that will allow you to explore the Configuration Search Space. These tools \
             may be found in the top right corner of the graph while your mouse is hovering over the graph. \
             In addition to the Download Tool, which downloads a the current graph, there are two types of tools available: \
             Selection Tools, and Visibility Tools. Selection Tools select configurations to be used on the testing page. \
             Visiblity Tools change the area of the graph shown."),
    html.Br(),
    html.Div("The functionality of each tool, listed from left to right, is below:"),
    html.Div(
        html.Ul([
            html.Li([html.Strong("Download: "), "The Download tool downloads the current version of the graph as a png file onto \
                     your computer."]),
            html.Li([html.Strong("Zoom: "), "The Zoom tool, a visibility tool, changes the area of the graph shown by zooming \
                     in on a subset of the feature space. By default, the Zoom tool is active. While the Zoom tool is active, click and \
                     drag on the chart to zoom in on the selected area. Double click on the chart to reset the view."]),
            html.Li([html.Strong("Pan: "), "The Pan tool, a visibility tool, changes the area of the graph shown by moving the center point \
                     of the graph. While the Pan tool is active, click and drag on the chart to move the center point. Double click on the \
                     chart to reset the view."]),
            html.Li([html.Strong("Box Select: "), "The Box Select tool, a selection tool, enables you to select configurations by drawing \
                     a box over the selections. While the Box Select tool is active, click and drag to draw a box to select configurations. \
                     Selected configurations will be denoted as black on the Configuration Search Space. After configurations are selected, \
                     they will be denoted by a checkmark in the Configuration Database on the right."]),
            html.Li([html.Strong("Lasso Select: "), "The Lasso Select tool, a selection tool, enables you to select configurations by drawing \
                     a free-form shape over the configuration points. While the Lasso Select tool is active, click and drag to draw a free-form \
                     shape to select configurations, and release the click-and-drag operation when the desired configurations are selected. \
                     Selected configurations will appear as black on the Configuration Search Space. After configurations are selected, they \
                     will be denoted by a checkmark in the Configuration Database on the right."]),
            html.Li([html.Strong("Zoom In: "), "The Zoom In tool, a visbility tool, changes the area of the graph shown by zooming in on the \
                     center of the graph."]),
            html.Li([html.Strong("Zoom Out: "), "The Zoom Out tool, a visibility tool, changes the area of the graph shown by zooming out from \
                     the center of the graph."]),
            html.Li([html.Strong("Autoscale: "), "The Autoscale tool, a visibility tool, resets the area of the graph shown back to the default."]),
            html.Li([html.Strong("Reset Axes: "), "The Reset Axes tool, a visibility tool, resets the area of the graph shown back to the default."]),
        ])
    ),
]
OPTIMIZATION_HISTOGRAMS = [
    html.Div("Histograms show the number of occurences of a variable over a set of intervals. \
             The Y axis in a histogram is the number of occurences, and the X axis indicates the interval."),
    html.Br(),
    html.Div("Below, you will find one histogram for each of the Optimization Metrics selected on the Metrics page."),
    html.Br(),
    html.Div("Interacting with the slider below each histogram will filter the configurations found on the rest of the page. \
             Utilize the slider functionality to narrow the range of acceptable metrics for future testing.")
]
OPTIMIZATION_SUMMARY = [
    html.Div("The Optimization Summary page shows the results of the Optimization, and is used to select the optimal configuration(s) \
             to be tested on the Test page."),
    html.Br(),
    html.Div("In the Feature Exploration section, the results are shown in the form of a scatterplot. Here, you can \
             easily see the relationships between two variables and select specific configurations using either the \
             Box Select Tool or the Lasso Select Tool. The variables shown on each axis are modifiable using the respective dropdowns."),
    html.Br(),
    html.Div("In the Configuration Database section, the results are shown in the form of a table. Here, you can see the \
             selected configurations, select additional configurations, sort or filter based on each metric, \
             and see the numerical relationship between configurations. The selected configurations will be used later on the Test page."),
    html.Br(),
    html.Div("In the Optimization Histograms section, the results are shown in the form of histograms. Here, you can \
             filter the configurations using the sliders below each histogram. Filtered results will appear \
             as red on the histogram, and be filtered from the rest of the page."),
    html.Br(),
    html.Div("One strategy to selecting optimal configurations would be to:"),
    html.Div(
        html.Ol([
            html.Li(["Preemptively decide the priority and ideal values of each Optimization Metric"]),
            html.Li(["Using the Optimization Histograms, filter the highest priority Optimization Metric \
                     based on the ideal values for that optimization metric. Observe the relationship between this and the \
                     other metrics."]),
            html.Li(["Iteratively repeat Step 2 for each of the next highest priority Optimization Metrics, \
                     until each Optimization Metric has been filtered."]),
            html.Li(["Observe the resulting Configuration Search Space:"]),
            html.Ul([
                html.Li(["If configurations remain, consider the trade off between those configurations; \
                         a better value using one metric will likely come at the cost of a lower value in another metric. \
                         Use either the Box Select Tool or Lasso Select tool to select the ideal configurations. \
                         Notice that the selected configurations will appear as checked in the Configuration Database."]),
                html.Li(["If there are no configurations, beginning from the lowest priority Optimization Metric, \
                         loosen the restrictions on that metric using the slider below the corresponding Optimization Histogram \
                         by expanding the filter until configurations appear. Refer to the above point."]),
            ])
        ])
    ),
]