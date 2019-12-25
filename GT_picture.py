"""
/***************************************************************************
  GT_picture.py

  Python 3.x script that takes data from geotagged photos (in selected folder) and shows their location on a map
  (in a web browser using OpenStreetMap and OpenLayers).
  One can click the points and see attached photo.
  This script requires PyQT5 and exif modules.
  Photo files with .jpg or .jpeg extension.

  version: 0.0.2
  
  --------------------------------------
  Date : 23.12.2019
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


import os, sys
import time
import urllib.request as ur
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from exif import Image
from Lat_Lon_extractor import Lat_Lon_extractor
import subprocess
import configparser


		
#========================================================================================================

class GT_picture(QWidget):


    RESULT_FILE_NAME_PREFIX = 'RSULT_site_'


    def __init__(self):
        super().__init__()
        self.lat_Lon_extractor = Lat_Lon_extractor()
        self.feature_quantity = 0
        self.sum_lat_float = 0.0
        self.sum_lon_float = 0.0
        self.www_folder_parh = os.path.join(os.path.dirname(__file__), 'www')
        self.INCLUDE_1_INDICATOR = None
        self.INCLUDE_2_INDICATOR = None
        self.THE_PLACE_TO_PASTE_INDICATOR = None
        self.WEB_BROWSER_PATH = None
        self.STOP_AT_THE_END = True
        self.PATTERN_SOURCE = None
        try:
            config = configparser.ConfigParser()
            config.read('Setup.txt')
            sections = config.sections()
            for section in sections:
                if section == 'GENERAL':
                    try:
                        self.INCLUDE_1_INDICATOR = self._get_string_from_config(config, section, 'INCLUDE_1_INDICATOR').strip()
                    except:
                        print('Setup PROBLEM: there is no INCLUDE_1_INDICATOR.')
                    try:
                        self.INCLUDE_2_INDICATOR = self._get_string_from_config(config, section, 'INCLUDE_2_INDICATOR').strip()
                    except:
                        print('Setup PROBLEM: there is no INCLUDE_2_INDICATOR.')
                    try:
                        self.THE_PLACE_TO_PASTE_INDICATOR = self._get_string_from_config(config, section, 'THE_PLACE_TO_PASTE_INDICATOR').strip()
                    except:
                        print('Setup PROBLEM: there is no THE_PLACE_TO_PASTE_INDICATOR.')
                elif section == 'USER':
                    try:
                        self.WEB_BROWSER_PATH = self._get_string_from_config(config, section, 'WEB_BROWSER_PATH').strip()
                    except:
                        print('Setup PROBLEM: there is no WEB_BROWSER_PATH.')
                    try:
                        self.STOP_AT_THE_END = self._get_string_from_config(config, section, 'STOP_AT_THE_END').strip() == 'yes'
                    except:
                        print('Setup PROBLEM: there is no STOP_AT_THE_END.')
                    try:
                        self.PATTERN_SOURCE = self._get_string_from_config(config, section, 'PATTERN_SOURCE').strip()
                    except:
                        print('Setup PROBLEM: there is no PATTERN_SOURCE.')
        except Exception as e:
            print('configparser Exception: ' + str(e))
        if self.INCLUDE_1_INDICATOR and self.INCLUDE_2_INDICATOR and self.THE_PLACE_TO_PASTE_INDICATOR and self.WEB_BROWSER_PATH and self.PATTERN_SOURCE:
            self.work()
        else:
            print('Setup PROBLEM: THE_PLACE_TO_PASTE_INDICATOR = ' + str(self.THE_PLACE_TO_PASTE_INDICATOR) + ', WEB_BROWSER_PATH = ' + str(self.WEB_BROWSER_PATH) + ', INCLUDE_1_INDICATOR = ' + str(self.INCLUDE_1_INDICATOR) + ', INCLUDE_2_INDICATOR = ' + str(self.INCLUDE_2_INDICATOR) + ', PATTERN_SOURCE = ' + str(self.PATTERN_SOURCE))
        print('feature quantity = ' + str(self.feature_quantity))
        if self.STOP_AT_THE_END:
            input('Press Enter to exit:')
        sys.exit()
        

    def work(self):
        result_file_path = None
        result_file = None
        self.remove_old_www_files()
        try:
            geotagged_pictures_folder = str(QFileDialog.getExistingDirectory(self, "Select geotagged pictures folder:"))
            print(geotagged_pictures_folder)
            img_file_names = [f for f in os.listdir(geotagged_pictures_folder) if os.path.isfile(os.path.join(geotagged_pictures_folder, f)) and (os.path.splitext(f)[1].upper() == '.JPG' or os.path.splitext(f)[1].upper() == '.JPEG')]
            html_include_points = ''
            for img_file_name in img_file_names:
                data_tuple = self.get_data_fom_image(os.path.join(geotagged_pictures_folder, img_file_name))
                if data_tuple:
                    print(','.join(data_tuple))
                    if self.feature_quantity > 0:
                        html_include_points += '\n\t\t\t\t'
                    html_include_points += str(self.get_html_point_code(data_tuple)) + '\n'
                else:
                    print('NO DATA')
            start_lat = self.sum_lat_float / float(self.feature_quantity)
            start_lon = self.sum_lon_float / float(self.feature_quantity)
            html_include_points += '\n\t\t\t\tvar start_point = ol.proj.fromLonLat([' + str(start_lon) + ', ' + str(start_lat) + ']);\n'
            html_include_points += '\t\t\t\tvar zoom = 15;\n'
            html_include_points += "\t\t\t\tvar pictures_folder_path = 'file://" + geotagged_pictures_folder + "/';\n"
            include_1_text = self.read_text_from_file(os.path.join(self.www_folder_parh, 'INCLUDE_1.txt'))
            include_2_text = self.read_text_from_file(os.path.join(self.www_folder_parh, 'INCLUDE_2.txt'))
            html_site_PATTERN_text = self.read_text_from_url(self.PATTERN_SOURCE)
            html_site_PATTERN_text = self.include_text(html_site_PATTERN_text, self.INCLUDE_1_INDICATOR, include_1_text)
            if not html_site_PATTERN_text:
                return
            html_site_PATTERN_text = self.include_text(html_site_PATTERN_text, self.INCLUDE_2_INDICATOR, include_2_text)
            if not html_site_PATTERN_text:
                return
            html_site_PATTERN_text = self.include_text(html_site_PATTERN_text, self.THE_PLACE_TO_PASTE_INDICATOR, html_include_points)
            if not html_site_PATTERN_text:
                return
            result_file_path = os.path.join(self.www_folder_parh, self.RESULT_FILE_NAME_PREFIX + time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time())) + '.html')
            result_file = open(result_file_path, 'w')
            result_file.write(html_site_PATTERN_text)
            result_file.close()
            result_file = None
        except Exception as e:
            print('work Exception: ' + str(e))
        finally:
            if result_file:
                result_file.close()
        if result_file_path:
            args = [self.WEB_BROWSER_PATH, '-new-tab', result_file_path]
            subprocess.call(args)
        else:
            print('There is no result_file_path.')
        
        
    def get_data_fom_image(self, image_path):
        try:
            with open(image_path, 'rb') as image_file:
                img = Image(image_file)
                img_lat_str = self.lat_Lon_extractor.get_lat_lon_str(img.gps_latitude)
                img_lon_str = self.lat_Lon_extractor.get_lat_lon_str(img.gps_longitude)
                time_stamp_str = img.datetime_original
                file_names = os.path.basename(image_path)
                return (img_lat_str, img_lon_str, time_stamp_str, file_names)
        except Exception as e:
            print('get_data_fom_image Exception: ' + str(e))
        return None


    def get_html_point_code(self, data_tuple):
        try:
            self.feature_quantity += 1
            self.sum_lat_float += float(data_tuple[0])
            self.sum_lon_float += float(data_tuple[1])
            return """var point_""" + str(self.feature_quantity) + """_feature = new ol.Feature
                    ({
                            geometry: new ol.geom.Point(ol.proj.fromLonLat([""" + data_tuple[1] + """, """ + data_tuple[0] + """])),
                            file_name: '""" + data_tuple[3] + """',
                            time_stamp: '""" + data_tuple[2] + """',
                            used: 'False'
                    });
                    point_feature_array.push(point_""" + str(self.feature_quantity) + """_feature);"""
        except Exception as e:
            print('get_html_point_code Exception: ' + str(e))
            print('Exception with ' + str(data_tuple) + '\n')
            return "console.log('Exception with " + str(data_tuple) + "');\n"
        

    def read_text_from_url(self, source):
        if source.startswith('http'):
            response = ur.urlopen(source)
            page_source = str(response.read())
            page_source = page_source.replace("b'", '')
            page_source = page_source.replace('\\t', '\t')
            page_source = page_source.replace('\\r\\n', '\r\n')
            page_source = page_source.replace('\\n', '\n')
            page_source = page_source.replace('\\r', '\r')
            page_source = page_source.replace("\\'", "'")
            return page_source
        else:
            return self.read_text_from_file(os.path.join(self.www_folder_parh, source))


    def read_text_from_file(self, file_path):
        text = None
        tmp_file = None
        try:
            tmp_file = open(file_path, 'r')
            text = tmp_file.read()
        except Exception as e:
            print('read_text_from_file Exception: ' + str(e))
        finally:
            if tmp_file:
                tmp_file.close()
        return text


    def include_text(self, base_text, indicator, include_text):
        if not indicator in base_text:
            print('ERROR: there is no indicator in base_text.')
            return None
        if include_text:
            return base_text.replace(indicator, include_text)
        else:
            print('ERROR: there is no include_text.')
            return None
            

    def remove_old_www_files(self):
        www_files_to_remove = [f for f in os.listdir(self.www_folder_parh) if os.path.isfile(os.path.join(self.www_folder_parh, f)) and f.startswith(self.RESULT_FILE_NAME_PREFIX)]
        print('www_files_to_remove = ' + str(www_files_to_remove))
        for www_file_to_remove in www_files_to_remove:
            os.remove(os.path.join(self.www_folder_parh, www_file_to_remove))


    def _get_string_from_config(self, config, section, key):
        if key in config[section]:
            return config[section][key]
        else:
            print("_get_string_from_config ERROR: there is no " + key + " in " + section + " section.")
            return None
        

#========================================================================================================


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gtp = GT_picture()
    sys.exit(app.exec_())
