Developer Notes
===============

Plan for Feburary, 2021
-----------------------

Steps:


  * Start using GitHub Automation

  * Start updating PyPi with each merge to "Master"

  * Automate versioning for developer versus production builds

  * Work on automated testing for gatekeeping prior to PyPi publication.

  * Backfill automated testing for USB functionality, that can be run inside GitHub

  * Checkout Python package on more systems and gracefully degrade.

  * Publish documentation on Read-the-Docs.


Getting Started with GitHub Automation
--------------------------------------

Used the 'Actions' button in GitHub, and selected the **Publish Python Package** workflow.
For now, just took things as they are, and then merged newly created file in the
branch that I had created for this story.  Pulling from the repository back to Wendy
showed this newly created file:

.. code-block:: console

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/packaging$ git pull
  remote: Enumerating objects: 6, done.
  remote: Counting objects: 100% (6/6), done.
  remote: Compressing objects: 100% (4/4), done.
  remote: Total 6 (delta 0), reused 0 (delta 0), pack-reused 0
  Unpacking objects: 100% (6/6), 2.08 KiB | 2.08 MiB/s, done.
  From github.com:rich-dobbs-13440/astutus
    ef33b12..3111c40  story_improve_ci_cd -> origin/story_improve_ci_cd
  Updating ef33b12..3111c40
  Fast-forward
  .github/workflows/python-publish.yml | 31 +++++++++++++++++++++++++++++++
  1 file changed, 31 insertions(+)
  create mode 100644 .github/workflows/python-publish.yml

The next task is to define the secrets for publishing inside of the GitHub repository.

Try publishing manually again, to refresh memory of tasks.

My pypi username: rich.dobbs.13440

At this time, manual upload worked:

.. code-block:: console

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/packaging/dist$ twine upload astutus-0.1.8-py3-none-any.whl
  Uploading distributions to https://upload.pypi.org/legacy/
  Enter your username: rich.dobbs.13440
  Enter your password:
  Uploading astutus-0.1.8-py3-none-any.whl
  100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3.11M/3.11M [00:07<00:00, 428kB/s]

  View at:
  https://pypi.org/project/astutus/0.1.8/
  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/packaging/dist$

Changed the password on PyPi to a truely random generated on Wendy using:

.. code-block:: console

  openssl rand -base64 32

|done| Stored this as a repository secret on Github with the name PYPI_PASSWORD.

|done| Tweak the Astutus version number, and start trying to use the workflow.

On the main page of https://github.com/rich-dobbs-13440/astutus, there
is a section called Releases and another that is called Packages.  My guess
is that I need to create a release, and then publish the package.  This would
be using the workflow, but triggering it manually.  A good step towards
CI/CD.

Tried to publish first package, but it says 0 packages.  Will probably need to
get automation working to build the package and place it in the correct location.

Added the Python package workflow to branch.  Will try get it to run.  Will probably
need to disable things within pytest.

Sphinx Preview Broken Currently
-------------------------------

As of 2021 01 27, the preview inside of Visual Studio Code is broken because interaction
between the preview and the Astutus Sphinx Extension.

.. code-block:: console

  Detailed error message
  Error
  Command failed: "/home/rich/src/github.com/rich-dobbs-13440/astutus/venv/bin/python" -m sphinx -b html . "/home/rich/src/github.com/rich-dobbs-13440/astutus/docs/_build/html"

  Extension error:
  Handler  for event 'build-finished' threw an exception (exception: [Errno 17] File exists: '/home/rich/src/github.com/rich-dobbs-13440/astutus/docs/_build/astutus_dyn_styled_templates')

  Error: Command failed: "/home/rich/src/github.com/rich-dobbs-13440/astutus/venv/bin/python" -m sphinx -b html . "/home/rich/src/github.com/rich-dobbs-13440/astutus/docs/_build/html"

  Extension error:
  Handler  for event 'build-finished' threw an exception (exception: [Errno 17] File exists: '/home/rich/src/github.com/rich-dobbs-13440/astutus/docs/_build/astutus_dyn_styled_templates')

    at ChildProcess.exithandler (child_process.js:304:12)
    at ChildProcess.emit (events.js:223:5)
    at maybeClose (internal/child_process.js:1021:16)
    at Process.ChildProcess._handle.onexit (internal/child_process.js:283:5)


  Extension error:
  Handler  for event 'build-finished' threw an exception (exception: [Errno 17] File exists: '/home/rich/src/github.com/rich-dobbs-13440/astutus/docs/_build/astutus_dyn_styled_templates')

Probably need to turn off execution of the post processing when the build is triggered by the preview.