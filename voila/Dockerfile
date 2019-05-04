FROM jupyter/base-notebook

RUN conda install ipywidgets ipympl pandas matplotlib voila
RUN jupyter nbextension install --user --py voila
RUN jupyter nbextension enable --user --py voila
