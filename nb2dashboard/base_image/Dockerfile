FROM jupyter/base-notebook

USER jovyan

# Common packages
RUN pip install ipydeps ipykernel ipywidgets pandas matplotlib

# Voila
EXPOSE 8866
RUN pip install voila

# nbparameterise
EXPOSE 3131
RUN pip install htmlgen jupyter_client nbparameterise
RUN \
  cd /opt/conda/bin && \
  wget https://raw.githubusercontent.com/takluyver/nbparameterise/master/examples/htmlform.py && \
  wget https://raw.githubusercontent.com/takluyver/nbparameterise/master/examples/webapp.py -O nbparameterise && \
  chmod +x nbparameterise
