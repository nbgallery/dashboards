FROM jupyter/base-notebook

RUN pip install ipython_blocking ipywidgets ipympl pandas matplotlib voila
RUN jupyter nbextension install --user --py voila
RUN jupyter nbextension enable --user --py voila
