# Voila/papermill notebook runner

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nbgallery/dashboards/master?filepath=papermill%2Fnotebook-runner.ipynb)

## Use case

Suppose you wrote a notebook in a exploratory, linear style, and now you want to share it with colleagues (or "productionize" it) as a standalone [Voila](https://voila.readthedocs.io/en/stable/) dashboard.  However, your input data isn't static -- you need to get some things from the user right up front, like database credentials and query parameters.  So you need some input widgets and a "Go!" button, but now you have to refactor your notebook to use callbacks, and you lose some of the readability and maintainability that makes notebooks so great.  How do you get the best of both worlds?  

*(For a more thorough examination of this use case, see this [discourse post](https://discourse.jupyter.org/t/thoughts-and-experiences-from-using-jupyter-in-enterprise/2572) and this repo's [README](https://github.com/nbgallery/dashboards/blob/master/README.md#our-use-case-for-dashboards).)*

## Goals of this demo
 * Generate "rich input" (i.e. widgets for the user to enter the parameters) but without requiring a lot of widget work
 * Avoid needing to refactor the notebook into callbacks
 * Support running in Voila - specifically, if there are other widgets (not counting our input widgets) that require the kernel, those will still work

## How this works

We add a "runner" notebook that does the following:

 1. Given a target notebook, use [Papermill](https://papermill.readthedocs.io/en/latest/) to extract the parameters.  This just requires the notebook author to list all the input parameters in a single code cell with default values.
 2. Generate a widget GUI for the parameters extracted by Papermill.  We do this with the [ipywidgets interact functions](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html).
 3. Use Papermill to inject those parameters back into the target notebook.
 4. Run the target notebook cell by cell and display its outputs in the runner notebook.  This is done by calling `get_ipython().ex()` on each cell and capturing the output with an [Output widget](https://ipywidgets.readthedocs.io/en/stable/examples/Output%20Widget.html).

In addition, Voila now provides access to the dashboard's URL via `$QUERY_STRING`, which lets us "bookmark" the runner notebook with a specific target notebook and parameter values.

## Limitations

 1. The input GUI is limited to what `ipywidgets.interactive` will automatically generate.  Obviously you could write a custom widget GUI by hand, but that's a lot of work.  You could probably use ipywidgets `interactive_output` and still re-use a lot of code here, but you lose the generic nature of the runner notebook.  A nice middle ground might be a way to specify simple metadata like widget type and value ranges (e.g. min/max for sliders) but without having to build the whole widget layout manually.
 2. The way the target notebook gets executed means you're limited to Python and you can't use magics.  But the more significant difference is that the last thing in the cell isn't automatically rendered; you have to explicitly `IPython.display` it.  Possibly you could overcome this by using Papermill's own execute functionality or by using [nbclient](https://nbclient.readthedocs.io/en/latest/index.html).  But then there's a second kernel in play so I don't know if it would work in Voila anymore (assuming the target notebook has other widgets that still require the kernel).
 
 ## Prior art
 
  * [nbparameterise](https://github.com/takluyver/nbparameterise) has an [example](https://github.com/takluyver/nbparameterise/blob/master/examples/webapp.py) to extract parameters and build a web form for a notebook.
  * [notebook_restified](https://github.com/kafonek/notebook_restified) uses a similar "two-notebook model" where the target notebook is treated as a REST interface that returns a value to the calling notebook.
  * [Callable cells](https://github.com/nbgallery/dashboards/blob/master/voila/magic_callbacks.ipynb) (in this repo) is an experiment to make cells callable without having to refactor them into functions.
  * Declarative widgets (now retired; see [repo](https://github.com/jupyter-attic/declarativewidgets) or [JEP](https://jupyter.org/enhancement-proposals/18-jupyter-declarativewidgets-incorporation/jupyter-declarativewidgets-extension-incorporation.html)) looked at creating rich inputs for notebooks in an easy and flexible way.
  * [Prototype Papermill support in Voila](https://github.com/voila-dashboards/voila/pull/484)
