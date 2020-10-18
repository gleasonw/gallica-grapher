# The Gallica Grapher
A tool to graph word-frequency data from the French national library's Gallica database. 

A user-friendly interface has yet to be implemented, but I plan to make this a web application. Currently, the code runs via commandline with GaliccaMainDriver as the main file.

E.G., python3 gallicaMainDriver.py brazza all 1830-1860 bar true true

This would give a graph of the word frequency of "Brazza" in over 1000 French newspapers from 1830-1860. The 'true' parameters determine if the graph will appear 
on a unique page and a unique graph, respectively. 
