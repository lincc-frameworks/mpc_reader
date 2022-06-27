# mpc_reader
A reader for 80 column MPC format

Requires astropy.

Reads the data into astropy SkyCoord and Time data structures. Performs online filtering by position, time, object name, or observatory code, allowing the user to load only a subset of the data at a time. The code includes a helper function that does the same filtering, but writes out to a file instead.
