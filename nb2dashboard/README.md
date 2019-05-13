# nb2dashboard

The goal of nb2dashboard is to take a single notebook and convert it into a docker image that presents the notebook as a dashboard without any ability to modify the code.  For dashboarding options, we have looked at [nbparameterise](https://github.com/takluyver/nbparameterise) (using [this example](https://github.com/takluyver/nbparameterise/blob/master/examples/webapp.py)) and [voila](https://github.com/QuantStack/voila).

The [base_image](base_image) directory contains a docker image that incorporates voila, nbparameterise, and some common packages on top of the [jupyter/base-notebook](https://github.com/jupyter/docker-stacks/tree/master/base-notebook) image.  If you mount in a directory containing a notebook, the image is sufficient to launch a dashboard in either nbparameterise (on port 3131) or voila (on port 8866).  See the [docker-run script](https://github.com/nbgallery/dashboards/blob/master/nb2dashboard/base_image/docker-run) for details.
