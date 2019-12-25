"""
/***************************************************************************
  Lat_Lon_extractor.py

  Python 3.x script that takes latitude or longitude data from string, list or tuple and returns it as string in format (-)DD.DDDDDDDDDD.

  version: 0.1.1
  
  --------------------------------------
  Date : 15.12.2019
  Copyright: (C) 2019 by Piotr Michałowski
  Email: piotrm35@hotmail.com
/***************************************************************************
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as published
 * by the Free Software Foundation.
 *
 ***************************************************************************/
"""


#========================================================================================================

class Lat_Lon_extractor:


    def __init__(self):
        pass


    def get_lat_lon_str(self, lat_lon):
        if type(lat_lon) is str:
            lat_lon = lat_lon.split(' ')
        if type(lat_lon) is tuple:
            lat_lon = list(lat_lon)
        if type(lat_lon) is list:
            n = len(lat_lon)
            hemisphere_indicator = 1.0
            for i in range(n):
                if type(lat_lon[i]) is not str:
                    lat_lon[i] = str(lat_lon[i])
                lat_lon[i] = lat_lon[i].replace(',', '.')
                lat_lon[i] = lat_lon[i].replace('°', '')
                lat_lon[i] = lat_lon[i].replace('\'', '')
                lat_lon[i] = lat_lon[i].replace('\"', '')
                lat_lon[i] = lat_lon[i].replace('+', '')
                lat_lon[i] = lat_lon[i].upper()
                lat_lon[i] = lat_lon[i].strip()
                if lat_lon[i].startswith('-'):
                    lat_lon[i] = lat_lon[i].replace('-', '')
                    hemisphere_indicator = -1.0
            if n == 1 and self.is_float(lat_lon[0]):
                return str(hemisphere_indicator * float(lat_lon[0]))
            if n > 1:
                try:
                    res = 0.0
                    m = 0
                    for i in range(n):
                        if self.is_float(lat_lon[i]):
                            res += float(lat_lon[i]) / (60.0 ** m)
                            m += 1
                        else:
                            if lat_lon[i] == 'N' or lat_lon[i] == 'E':
                                hemisphere_indicator = 1.0
                            elif lat_lon[i] == 'S' or lat_lon[i] == 'W':
                                hemisphere_indicator = -1.0
                            else:
                                return None
                    return str(hemisphere_indicator * res)
                except:
                    pass
        return None


    def is_float(self, tx):
        try:
            f = float(tx)
            return True
        except:
            return False


#========================================================================================================


if __name__ == '__main__':

    # TEST:
    expected_value = [None] * 4
    test_value_tuple = [None] * 4
    expected_value[0] = '53.78397136666667'
    test_value_tuple[0] = ('53.78397136666667', '53 47.038282', '53 47 2.29692', 'N 53.78397136666667', 'N 53 47.038282', 'N 53 47 2.29692', '53.78397136666667 N', '53 47.038282 N', '53 47 2.29692 N')
    expected_value[1] = '-53.78397136666667'
    test_value_tuple[1] = ('-53.78397136666667', '-53 47.038282', '-53 47 2.29692', 'S 53.78397136666667', 'S 53 47.038282', 'S 53 47 2.29692', '53.78397136666667 S', '53 47.038282 S', '53 47 2.29692 S')
    expected_value[2] = '20.479126666666666'
    test_value_tuple[2] = ('20.479126666666666', '20 28.7475999999996', '20 28 44,855999999976', 'E 20.479126666666666', 'E 20 28.7475999999996', 'E 20 28 44,855999999976', '20.479126666666666 E', '20 28.7475999999996 E', '20 28 44,855999999976 E')
    expected_value[3] = '-20.479126666666666'
    test_value_tuple[3] = ('-20.479126666666666', '-20 28.7475999999996', '-20 28 44,855999999976', 'W 20.479126666666666', 'w 20 28.7475999999996', 'W 20 28 44,855999999976', '20.479126666666666 W', '20 28.7475999999996 W', '20 28 44,855999999976 W')

    lat_Lon_extractor = Lat_Lon_extractor()
    OK_n = 0
    ERROR_n = 0
    for i in range(4):
        print('expected_value = ' + expected_value[i] + '\n')
        for lat_lon in test_value_tuple[i]:
            print('\tlat_lon = ' + lat_lon)
            x = lat_Lon_extractor.get_lat_lon_str(lat_lon)
            print('\tx = ' + str(x))
            if lat_Lon_extractor.is_float(x):
                d = float(expected_value[i]) - float(x)
                print('\tdiff = ' + str(d))
                if abs(d) < 0.0000001:  # about 1cm
                    print('\tOK')
                    OK_n += 1
                else:
                    print('\tERROR(1)')
                    ERROR_n += 1
            else:
                print('\tERROR(2)')
                ERROR_n += 1
        print('\n')
    print('OK - ' + str(OK_n) + ', ERROR - ' + str(ERROR_n))
