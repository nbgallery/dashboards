# This Dockerfile roughly approximates how to get IRuby with widgets working in binder
FROM jupyter/base-notebook

# Packages for apt.txt
USER root
RUN apt update
RUN apt install -y libtool make libffi-dev libzmq3-dev libczmq-dev ruby ruby-dev

# Commands for postBuild script (no root/sudo)
USER jovyan
RUN gem install --user-install ffi-rzmq iruby erector
RUN ~/.gem/ruby/*/bin/iruby register
