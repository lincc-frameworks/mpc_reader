"""This module implements a filtered reader for MPC observations."""

from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u

class MPCFilteredReader():
    _name = None
    _ra_range = None
    _dec_range = None
    _time_range = None
    _mag_range = None
    _obscode = None

    def set_name(self, name):
        self._name = name

    def set_obscode(self, obscode):
        self._obscode = obscode
        
    def set_time_range(self, start_time, end_time):
        """
        Sets the time range of the filter to accept.

        Parameters
        ----------
        start_time: float
            The start time of the valid range in MJD.
        end_time: float
            The end time of the valid range in MJD.
        """
        if start_time > end_time:
            raise IllegalArgumentError("start_time must be >= end_time")
        self._time_range = (start_time, end_time)

    def set_skycoords_range(self, ra_min=0.0, ra_max=24.0,
                            dec_min=-90.0, dec_max=90.0):
        """
        Sets the coordinate range to pass through the filter
        in RA and dec.

        Parameters
        ----------
        ra_min: float
            The minimum RA to accept (in hours).
        ra_max: float
            The maximum RA to accept (in hours).
        dec_min: float
            The minimum dec to accept (in degrees).
        dec_max: float
            The maximum dec to accept (in degrees).  
        """
        if ra_min > ra_max:
            raise IllegalArgumentError("ra_min must be >= to ra_max")
        if dec_min > dec_max:
            raise IllegalArgumentError("dec_min must be >= dec_max")
        self._ra_range = (ra_min, ra_max)
        self._dec_range = (dec_min, dec_max)

    def set_magnitude_range(self, start, end):
        """
        Sets the magnitude range for the filter to accept.

        Parameters
        ----------
        start: float
            The start magnitude of the valid range.
        end: float
            The end magnitude of the valid range.
        """
        if start > end:
            raise IllegalArgumentError("start must be >= end")
        self._mag_range = (start, end)
        
    def parse_and_filter_line(self, line):
        """
        Parse a line of MPC observations, returning None if they are invalid or filtered.
        
        Parameters
        ----------
        line: str
            A single line of MPC formatted observations.
            
        Returns
        -------
        coord: astropy SkyCoord object
            A SkyCoord object with the ra, dec of the observations or
            None if the object is filtered.
        time: astropy Time object
            Time of the observation or None if the object is filtered.
        """
        filtered = False

        # Extract the time and filter on the time bounds (if needed).
        time = Time('%s-%s-%s' % (line[15:19], line[20:22], line[23:25]))
        time = time.mjd + float(line[25:31])
        if self._time_range and (time < self._time_range[0] or
                                 time > self._time_range[1]):
            filtered = True
            time = None

        # Extract the coordinates and filter (if needed).
        coord = None
        if not filtered:
            try:
                coord = SkyCoord(line[32:44], line[44:56], unit=(u.hourangle, u.deg))
            except ValueError:
                coord = None

            if coord:
                if self._ra_range and (coord.ra.hour < self._ra_range[0] or
                                       coord.ra.hour > self._ra_range[1]):
                    filtered = True
                if self._dec_range and (coord.dec.degree < self._dec_range[0] or
                                        coord.dec.degree > self._dec_range[1]):
                    filtered = True
            else:
                filtered = True

        # Filter on the name if needed.
        if not filtered and self._name:
            if self._name != str(line[0:12]).strip():
                filtered = True

        # Filter on the obscode if needed.
        if not filtered and self._obscode:
            if len(line) < 80:
                filtered = True
            elif line[77:80] != self._obscode:
                filtered = True

        # Filter on magnitude if needed.
        if not filtered and self._mag_range:
            if line[67] != '.':
                filtered = True
            else:
                mag = float(line[65:70])
                if mag < self._mag_range[0] or mag > self._mag_range[1]:
                    filtered = True
                
        if filtered:
            return None, None
        return coord, time


    def read_file(self, filename):
        """
        Read in a file with observations in MPC format and return
        the coordinates.
        
        Parameters
        ----------
        filename: str
            The name of the file with the MPC-formatted observations.
    
        Returns
        -------
        coords: List of astropy SkyCoord objects
            A list of SkyCoord objects with the ra, dec of the observations.
        times: List of astropy Time objects
            Times of the observations
        """
        coords = []
        times = []

        with open(filename, 'r') as f:
            for line in f:
                coord, time = self.parse_and_filter_line(str(line))
                if coord and time:
                    coords.append(coord)
                    times.append(time)
        return coords, times


    def filter_file(self, in_file, out_file):
        """
        Creates a MPC file that is a filtered subset of observations from the
        original MPC file. Used to pre-filter files.

        Parameters    
        ----------
        in_file: str
            The name of the input file with the MPC-formatted observations.
        out_file: str
            The name of the output file into which to write the filtered
            MPC-formatted observations.
        """    
        with open(in_file, 'r') as f_in:
            with open(out_file, 'w') as f_out:
                for line in f_in:
                    coord, time = self.parse_and_filter_line(str(line))
                    if coord and time:
                        f_out.write(line)
