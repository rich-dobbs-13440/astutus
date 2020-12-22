Developer Notes
===============

import astutus.web.flask_app
astutus.web.flask_app.run_with_standard_options()

This doesn't seem to work.  Instead just use main()

Plan:

* Create some REST API to drive adoption of Rasberry Pi into ecosystem.

* Transfer python package to RaspPi.

* Web inteface to control lights

* Pick out colors of lights with sensor

While OP might have a good reason for wanting to do exactly this, it usually is a bad idea (password can be read by ps, and so on) and I wanted to provide a more secure alternative.

A better solution if you want to run something with sudo without putting in your password is to allow your user to do exactly that one command without password.

Open sudoers file with sudo visudo and add the following line (obviously replace the username at the beginning and the command at the end):

alice ALL = NOPASSWD: /full/path/to/command

This is explained more here: https://askubuntu.com/a/39294


Linter rstcheck is not installed.


