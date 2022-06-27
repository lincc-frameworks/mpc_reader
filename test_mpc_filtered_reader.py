from astropy.time import Time
from mpc_filtered_reader import *
import unittest

class TestMPCFilteredReader(unittest.TestCase):

    # Test cases from the MPC NumObs.txt file:
    # https://www.minorplanetcenter.net/iau/ECS/MPCAT-OBS/MPCAT-OBS.html
    _test_cases = [
         '     Hall2    C1999 06 05.03484 17 47 47.64 -25 27 24.3          16.6 R      706',
         '     She001  2C1995 09 14.79817 23 29 42.54 -02 59 15.9          15.5 V      121',
         '     0000001  C2002 10 10.28966 01 45 43.18 +08 05 24.4                r     644',
         '     000007k ZC2009 07 12.38821 20 52 22.26 -16 47 54.1                r     I41',
         '     00000m3 ZC2009 07 22.38815 20 45 14.31 -17 34 51.4          21.8 Rr     I41']

    def _check_test_cases(self, reader, is_valid):
        self.assertEqual(len(self._test_cases), len(is_valid))
        for i in range(len(self._test_cases)):
            coord, time = reader.parse_and_filter_line(self._test_cases[i])
            passed = coord is not None
            self.assertEqual(passed, is_valid[i])

    def test_filter_on_name(self):
        reader = MPCFilteredReader()
        reader.set_name('Hall2')
        #self._check_test_cases(reader, [True, False, False, False, False])
        reader.set_name('0000001')
        #self._check_test_cases(reader, [False, False, True, False, False])

    def test_filter_on_obscode(self):
        reader = MPCFilteredReader()
        reader.set_obscode('706')
        #self._check_test_cases(reader, [True, False, False, False, False])
        reader.set_obscode('I41')
        #self._check_test_cases(reader, [False, False, False, True, True])

    def test_filter_on_time(self):
        reader = MPCFilteredReader()
        reader.set_time_range(Time('1999-06-04').mjd, Time('1999-06-06').mjd)
        #self._check_test_cases(reader, [True, False, False, False, False])
        reader.set_time_range(Time('2009-07-10').mjd, Time('2009-07-23').mjd)
        #self._check_test_cases(reader, [False, False, False, True, True])
        reader.set_time_range(Time('2009-07-22').mjd, Time('2009-07-22').mjd + 0.5)
        #self._check_test_cases(reader, [False, False, False, False, True])

    def test_filter_on_coord(self):
        reader = MPCFilteredReader()
        reader.set_skycoords_range(17.0, 21.0, -25.5, -15.0)
        self._check_test_cases(reader, [True, False, False, True, True])
        reader.set_skycoords_range(0.0, 5.0, 0.0, 10.0)
        self._check_test_cases(reader, [False, False, True, False, False])
        reader.set_skycoords_range(20.0, 21.0, -18.0, -16.0)
        self._check_test_cases(reader, [False, False, False, True, True])
        
    def test_filter_on_magnitude(self):
        reader = MPCFilteredReader()
        reader.set_magnitude_range(0.0, 25.0)
        self._check_test_cases(reader, [True, True, False, False, True])
        reader.set_magnitude_range(14.0, 18.0)
        self._check_test_cases(reader, [True, True, False, False, False])

if __name__ == '__main__':
    unittest.main()
