# nbgallery/dashboards

This repository contains various notes and experiments in Jupyter dashboarding.  Any code you find here may or may not be suitable for production.  We are definitely open to comments and suggestions, especially if we're doing something crazy, so please feel free to [open an issue](https://github.com/nbgallery/dashboards/issues/new) to give us feedback.

Our use case for Jupyter widgets and dashboards is a little different from what we tend to see in other organizations in the Jupyter community.  Our organization deals with a highly-regulated big data environment with two major constraints:

 * Each user has a different view of the data due to row- or even cell-level access permissions.
 * It is not always desirable (or feasible) to analyze all the data at once.
 
As an example, consider a large hospital, subject to [HIPAA](https://en.wikipedia.org/wiki/Health_Insurance_Portability_and_Accountability_Act) privacy regulations, where patient data may not be visible to all employees.  Suppose doctors can only see data about their own patients, while department heads can see records for all patients in their department.  Suppose administrators can view records for all patients, but only billing data; similarly, maybe the lab can view only test results.  Lastly, suppose the data science team can't view *any* data about real patients -- perhaps they only have access to notional or anonymized data.  So, when a data scientist writes a Jupyter notebook to look at, say, prescription trends, doctors who want to run that analysis must run the notebook themselves so that database access controls can limit the input data to their own patients.

The data access restrictions of our environment have led to two effects that we've found are somewhat unique:

 * We have significantly more Jupyter notebook *users* than notebook *authors*.  In our organization, we have thousands of users, but fewer than 20% have written a notebook themselves.  This has motivated a number of features in our notebook collaboration platform [nbgallery](https://nbgallery.github.io/): recommenders, code health monitoring, and peer review.
  * We tend to use Jupyter widgets less to manipulate output visualizations and more to create input forms for database queries.  These input forms prompt the user for parameters (say, patient gender and age), and the database returns only records that match the parameters *and* are viewable by the user running the notebook.  The consequence of this model is that notebook execution needs to block until the user submits the form.  Since ipywidgets do not block by default, this means we must structure our notebooks to use widget callback functions or something like [ipython_blocking](https://pypi.org/project/ipython-blocking/).
  
Our interest in dashboards is primarily motivated by two requirements:

 * Since many of our Jupyter users are non-coders, dashboards can lower the barrier to entry to the Jupyter platform.  The growing interest in dashboards across the Jupyter community is a reflection of the fact that this is not unique to our organization.
 * A number of dashboard solutions provide *immutable execution*, meaning the user cannot modify the code.  This may be important in regulated environments where the analysis needs to be approved before running in production.  In our hospital example, perhaps notebooks need to be vetted for HIPAA compliance before the data science team can release them for use by the doctors.
 
More generally on the immutable execution front, we're also interested in what we're calling "Notebook as a Service" (NaaS).  The idea here is that once the data scientist has finalized the algorithms and analysis in a notebook, you no longer need the interactivity of the native Jupyter interface, and the notebook can be treated as an immutable code artifact.  That enables various applications:
 
 * Creating user-friendly dashboards
 * Parameterizing notebooks as back-ends for existing tools and UIs
 * Parameterizing notebooks for use in cron jobs and pipelines
 * Using notebooks as a web service API
  
One of the questions we get when we talk about NaaS is if you don't need the interactive Jupyter interface, why use the notebook format at all?  If you need a cron job, why not a plain python script?  If you need a web app, why not Flask or Django?  The answer is that if the analysis was initially developed in a notebook, then it may just be easier and cheaper to keep it that way.  You need to have a compelling argument for re-engineering the solution in order to justify the time and labor costs.  Our experience has been similar to that of Zillow, who found that [it wasn't worth re-writing R analytics in C++ or Java](https://www.infoworld.com/article/3060773/hot-property-how-zillow-became-the-real-estate-data-hub.html).

Here are some NaaS-related projects that we've been tracking:

 * Dashboards
   * [Jupyter dashboards](https://github.com/jupyter/dashboards) and [dashboard server](https://github.com/jupyter-attic/dashboards_server) (inactive)
   * [Voila](https://github.com/QuantStack/voila)
   * [Appmode](https://github.com/oschuett/appmode)
   * [nbinteract](https://github.com/SamLau95/nbinteract)
 * Headless execution and parameterization
   * [Papermill](https://github.com/nteract/papermill)
   * [nbparameterise](https://github.com/takluyver/nbparameterise)
   * [PPExtensions](https://github.com/paypal/PPExtensions)
 * Notebooks as web APIs
   * [Kernel Gateway's http mode](https://jupyter-kernel-gateway.readthedocs.io/en/latest/http-mode.html)
