FROM jupyter/base-notebook
LABEL maintainer="https://github.com/nbgallery/dashboards"

USER jovyan

# Common packages
RUN pip install ipydeps ipympl ipywidgets pandas matplotlib

# Voila
EXPOSE 8866
RUN pip install voila

# nbparameterise
EXPOSE 3131
RUN pip install htmlgen nbparameterise
RUN \
  cd /opt/conda/bin && \
  wget https://raw.githubusercontent.com/takluyver/nbparameterise/master/examples/htmlform.py && \
  wget https://raw.githubusercontent.com/takluyver/nbparameterise/master/examples/webapp.py -O nbparameterise && \
  chmod +x nbparameterise
