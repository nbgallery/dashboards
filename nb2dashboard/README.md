# nb2dashboard

The goal of nb2dashboard is to take a single notebook and convert it into a docker image that presents the notebook as a dashboard without any ability to modify the code.  It's similar to [repo2docker](https://github.com/jupyter/repo2docker) but with fewer features and with a dashboard UI instead of the regular Jupyter notebook UI -- more specifically, *without access* to the Jupyter UI, in case we want to ensure users are running a vetted version of the code.  For dashboarding options, we have looked at [nbparameterise](https://github.com/takluyver/nbparameterise) (using [this example](https://github.com/takluyver/nbparameterise/blob/master/examples/webapp.py)) and [voila](https://github.com/QuantStack/voila).

The [base_image](base_image) directory contains a docker image that incorporates voila, nbparameterise, and some common packages on top of the [jupyter/base-notebook](https://github.com/jupyter/docker-stacks/tree/master/base-notebook) image.  If you mount in a directory containing a notebook, the base image is sufficient to launch a dashboard in either nbparameterise (on port 3131) or voila (on port 8866).  See the [docker-run script](https://github.com/nbgallery/dashboards/blob/master/nb2dashboard/base_image/docker-run) for details.

The [nb2dashboard](nb2dashboard.py) script takes it a step further by baking the notebook into its own image built on top of the base.  It supports 3 sources for notebooks: local file, remote URL, or remote URL in an [nbgallery](https://nbgallery.github.io) instance.  By default, the script will only stage the docker build in a subdirectory; add `--build` to actually build it (with sudo -- may prompt for your password).

For example, to convert the nbparameterise [Fibonacci example](https://github.com/takluyver/nbparameterise/blob/master/examples/Fibonacci.ipynb) into a dashboard:

```
./nb2dashboard.py --url https://raw.githubusercontent.com/takluyver/nbparameterise/master/examples/Fibonacci.ipynb --name fibonacci --mode nbparameterise --build

sudo docker run -p 3131:3131 --rm nb2dashboard-fibonacci
```

To convert one of this repo's voila examples:

```
./nb2dashboard.py --file ../voila/callback_matplotlib_widget_1.ipynb --name mpl --mode voila --build

sudo docker run -p 8866:8866 --rm nb2dashboard-mpl
```

The script will perform some light grooming on the input notebook:
 * Cells tagged with `nb2dashboard/ignore` will be removed.  This is useful if you have a widget UI for use in Jupyter proper but want to omit that when parameterizing the notebook.
 * A cell tagged with `parameters` will be moved to the top of the notebook.  This provides some compatibility for [papermill](https://github.com/nteract/papermill)-friendly notebooks.
 * A cell containing [ipydeps](https://github.com/nbgallery/ipydeps) will be removed and executed during docker build time instead of during runtime.  In our organization, we run an [extremely minimal docker image](https://github.com/nbgallery/jupyter-alpine), and we've established the convention of using ipydeps to install dependencies, which provides [some advantages](https://github.com/nbgallery/ipydeps/blob/master/README.md) over doing `!pip install` and is more user-friendly than opening a terminal.  However, this means that users have to wait for installation the first time they run a notebook (which can be slow on Alpine Linux, which lacks pre-compiled versions of many packages), so moving that into the docker build here eliminates that wait.
 
 There are a few features specific to our use of nbgallery:
  * You can build from an nbgallery notebook URL, which has slightly different behavior than a generic URL.
  * Some nbgallery metadata embedded in the downloaded notebook is converted into environment variables in the docker image.  This enables libraries to gather usage metrics.
