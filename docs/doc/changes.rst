Changes
=======

Here's where you find out what we are working on, and what we've worked on -- and you can now use!

.. astutus_toggle_note:: collapsed To the Developer

  To the developer:  With incremental, test-driven development, it should be possible to deliver
  `Frequent, Tangible, Working Results  <https://en.wikipedia.org/wiki/Peter_Coad>`_
  most days. You should be **concerned** if you haven't committed in a day.  You should probably
  **throw away your changes** and replan if you've gone two days without having something to
  push to the repository.  It is reasonable to see regular transitions between what's on your
  backlog, and what's done, and available for use as new features.  It is **concerning** if
  that is not happening.


What's Up
---------

Here's where you find what we are working on.  Rather we work on something else?  Just
let us know!

.. astutus_toggle_note:: collapsed To the Developer

  To the developer:  Your **backlog** should consist of epics, stories, tasks, and spikes. For planning purposes,
  your backlog shouldn't be too large and it shouldn't be too small.  You'll need to
  at least one epic on it, and I don't understand why you'd need more than two!
  Stories tell where you're headed, and tasks get you there. Spikes are for deciding
  what to do, and helping you know how long until you get there.

  At any point, it should be possible for a smart manager to look at your backlog,
  understand what you are trying to get done, what sort of things that you are
  currently working on, and whether you are about done.

  By looking at your backlog over time, it should be possible for a smart manager
  to understand about where you'll be at in the future, without having to
  trust your assessment (which is probably over-optimimistic!).

  Chances are, you should be adding tasks after each commmit, as you discover
  new tasks, plan new work, or get to the point where you want to communicate
  details of the work required.


Backlog:

  * |in_progress| Task: Useful defaults if .. astutus_dyn_destination::  is omitted.
  * Story: Polish sphinx extension so that it is good-enough to be used by others.
  * Task: Style Raspberry Pi ifconfig page.
  * Add a progress list directive.
  * Task: Provide a link to the RPi's astutus-web-app.
  * Task: Have an indication that publish wheels is proceding.
  * Task: Fetch Wheels from Internet from Flask App - At least for same platform.
  * Task: Mark relay tests as slow.
  * Task: Get color sensor working on RPi.
  * Task: Write test with relays controlling lights and monitored by color sensor.
  * Task: Some tests of USB devices that are independent of current /sys/devices structure.
  * Epic: Get repository good enough to be publically visible.


What's New
----------

Here is where you'll find a record of what things have gotten done.  Not a lot of
hand waving, but not as detailed as repository commits.

.. astutus_toggle_note:: collapsed To the Developer

  To the developer: Just move items from the backlog to here as you make commits.

Done:

  * |newly_done| 2021-01-24 16:22 Task: Cleanup and generalize reading and processing of post processing directives.
  * |done| 2021-01-24 13:03 Task: Keep HTML lines as list in post processing, rather than combining and splitting.
  * |done| 2021-01-24 11:56 Task: Work out search page with new structure.
  * |done| 2021-01-24 11:56 Task: Work out Index with new structure.
  * |done| 2021-01-24 11:56 Task: Work out module Index with new structure.
  * |done| 2021-01-24 11:56 Task: Generalize inclusion of new header material for astutus dynamic pages.
  * |done| 2021-01-23 17:18 Task: Automate generation of breadcrumbs for dynamic pages.
  * |done| 2021-01-23 10:00 Task: Backout dead javascript and Sphinx extension code
  * |done| 2021-01-23 09:07 Task: Use id's rather than direct docnames for identifying dynamic replacements.
  * |done| 2021-01-22 12:27 Task: Move Toggle styling to a static CSS file.
  * |done| 2021-01-22 11:24 Task: Handle markup within astutus_toggle_note content.
  * |done| 2021-01-22 09:31 Task: Directive astutus_toggle_note working in basic form.
  * |done| 2021-01-21 12:31 Task: Fix up indentation so that it does better with Javascript
  * |done| 2021-01-21 11:15 Spike: Try handling navigation to dynamic pages in flask. Successful, can be merged.
  * |done| 2021-01-20 10:13 Task: Fix bug with other page's vertical menu not substituting for dynamic templates.
  * |done| 2021-01-20 06:40 Task: Move most post processing out of packaging into Sphinx extension and use it from there.
  * |done| 2021-01-19 21:33 Task: Convert «« »» markup into Sphinx directives.
  * |done| 2021-01-19 15:36 Task: Polish up device names
  * |done| 2021-01-19 14:09 Task: For item dynamic pages, fix up vertical menu, both for item and parent.
  * |done| 2021-01-18 01:01 Task: For dynamic pages, need to fix up vertical menu links back to docs.
  * |done| 2021-01-18 01:01 Task: Update UI for dynamic pages.  Do a round of clean up and polish.
  * |done| 2021-01-17 18:23 Task: Sphinx toctrees automatic for dynamic web pages.
  * |done| 2021-01-17 13:51 Spike: Suppress vertical menu replacement, and understand how vertical menu is defined.
  * |done| 2021-01-17 10:22 Task: Sphinx toctree entries to dynamic web pages.
  * |done| 2021-01-16 10:43 Story: As a developer, I can view documentation from RPi
  * |done| 2021-01-16 10:43 Task: Implement command to launch flask app.
  * |done| 2021-01-15 16:28 Task: Install Astutus on Rpi without internet.
  * |done| 2021-01-15 10:31 Task: Publish wheels to RPi.
  * |done| 2021-01-14 21:53 Task: Provide decent titles for dynamic pages suitable for book marking.
  * |done| 2021-01-14 14:24 Task: Custom favicon for documentation pages.
  * |done| 2021-01-14 13:19 Task: Get search to work from dynamic page without Javascript error.
  * |done| 2021-01-14 12:48 Task: Reduce usage of Jquery.  Use vanilla Javascript techniques instead.
  * |done| 2021-01-14 12:02 Task: Style /astutus/raspi/ifconfig page. (Gets rid of generic page with a JQuery ajax call)
  * |done| 2021-01-14 03:40 Task: Fix regressions with devices page.
  * |done| 2021-01-13 12:33 Task: Implement OnClick for device with ajax page.
  * |done| 2021-01-13 12:33 Task: Speedup rendering of device tree page.
  * |done| 2021-01-13 12:33 Task: Rework structure of device aliases file and DeviceAliases class.
  * |done| 2021-01-10 10:01 Task: Refactor popup dialog templating for better reuse.
  * |done| 2021-01-10 08:07 Task: Add data and instructions to Add alias dialog in tree display.
  * |done| 2021-01-09 22:28 Task: Single source version number between code, package, and documentation.
  * |done| 2021-01-09 20:28 Story: As a Flask developer, I need to be able to control logging by module at runtime.
  * |done| 2021-01-09 20:28 Task: In flask_app, connect up with loggers enumerated by module, and set log level.
  * |done| 2021-01-09 20:28 Task: Persist desired level of loggers in database.
  * |done| 2021-01-09 17:21 Task: Handle dynamic changing of log levels via web page.
  * |done| 2021-01-09 12:47 Task: Create an /astutus/log page that lists the modules with loggers.
  * |done| 2021-01-09 07:34 Task: Clean up handling of top of tree.  Visual layout + adding, deleting aliases.
  * |done| 2021-01-08 08:22 Task: Add an initial favicon to website.  Mechanics working.  Image needs work.
  * |done| 2021-01-07 22:49 Task: Clean up add alias form on device tree. Background colors and padding.
  * |done| 2021-01-07 22:02 Task: Get basic placeholder insertion to work.
  * |done| 2021-01-06 20:05 Task: Polish browser presentation of USB tree.
  * |done| 2021-01-06 14:54 Story: Implement a USB print tree command for package.
  * |done| 2021-01-06 14:54 Story: As a user, I can configure my own aliases for physical USB devices.
  * |done| 2021-01-06 14:54 Task: Add ability to edit alias.
  * |done| 2021-01-06 14:54 Task: Get rid of Colorama; replace with webcolors.
  * |done| 2021-01-05 12:36 Task: Display Device Configurations.
  * |done| 2021-01-04 22:01 Task: Add links to /astutus/usb.
  * |done| 2021-01-04 19:07 Task: Add ability to delete an alias.
  * |done| 2021-01-04 12:50 Task: Refactor: Move USB and Raspberry Pi to Flask Blueprints.
  * |done| 2021-01-04 05:18 Task: Apply alias, styling to USB page, and get rid of unneed data attributes.
  * |done| 2021-01-03 18:57 Task: Show alias contents on USB page.
  * |done| 2021-01-03 02:05 Task: Handle form submission add or update alias and rewrite file.
  * |done| 2021-01-03 12:15 Task: Implement Cancel function for add alias form.
  * |done| 2021-01-03 01:56 Task: Display USB tree in browser.
  * |done| 2021-01-01 23:49 Task: Style /astutus/raspi/item page.
  * |done| 2021-01-01 22:17 Task: Style /astutus/raspi find page.g
  * |done| 2021-01-01 15:10 Task: Style /astutus page.
  * |done| 2021-01-01 11:22 Task: First pass at displaying USB device tree with Jinja2 template include.
  * |done| 2020-12-31 19:30 Spike: Try to use Sphinx to generate a styled base for a Jinja2 template.
  * |done| 2020-12-30 20:13 Task: Create a verbose mode for the astutus-usb-tree
  * |done| 2020-12-29 19:13 Epic: Get package available on PyPi
  * |done| 2020-12-29 18:17 Task: Create the docstring for the DeviceAliases class.
  * |done| 2020-12-29 14:51 Task: Create an initial pass for module docstring for astutus.usb.tree
  * |done| 2020-12-29 12:00 Task: Update for autodocs for all modules.
  * |done| 2020-12-29 09:16 Story: As a user, I can run a command to view the USB tree.
  * |done| 2020-12-28 13:06 Story: As a developer, the database is operational in the Flask App.
  * |done| 2020-12-27 21:42 Story: As a developer, I have instructions on how to build the package.
  * |done| 2020-12-27 10:50 Use selector searches to allow relay test to work after rebooting.
