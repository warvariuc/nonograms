#!/usr/bin/env python3
import sys

from nonograms.start import app

res = app.exec()  # start the event loop
sys.exit(res)
