# ---------------------------------------------------------------------
# Copyright (c) 2018 TU Berlin, Communication Systems Group
# Written by Tobias Senst <senst@nue.tu-berlin.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
import os
import glob
try:
    from itertools import tee, izip
except ImportError:
    pass

def window(iterable, size):
    iters = tee(iterable, size)
    for i in range(1, size):
        for each in iters[i:]:
            next(each, None)
    return zip(*iters)

class SDataBaseParser:
    def __init__(self):
        self.filenames_dict = list()

class CrowdFileParser(SDataBaseParser):
    def __init__(self):
        SDataBaseParser.__init__(self)

    def parseFilenames(self, basepaths):
        self.filenames_dict = []
        for dirpath, dirnames, filenames in os.walk(basepaths["images"]):
            for dirs in dirnames:
                image_paths = glob.glob("{}/*.png".format(dirpath + dirs))
                image_paths1 = glob.glob("{}/*.jpg".format(dirpath + dirs))
                image_paths = image_paths + image_paths1
                image_paths = sorted(image_paths)  # assume filenames are sortable
                image_pairs = list(window(image_paths, 2))
                for image_pair in image_pairs:
                    #print(image_pair)
                    filename_dict = dict()
                    filename_dict["prevImg"] = image_pair[0]
                    filename_dict["currImg"] = image_pair[1]
                    filename_base = os.path.relpath(filename_dict["prevImg"], dirpath + dirs )
                    filename_base = os.path.splitext(filename_base)[0]



                    if "groundtruth" in basepaths:
                        filenumber = filename_base.split("_")[1]
                        filename_dict["gtflow"] = basepaths["groundtruth"] +  "/" + dirs +  "/frameGT_" + filenumber + ".flo"
                    if "masks" in basepaths:
                        filenumber = filename_base.split("_")[1]
                        filename_dict["mask"] = basepaths["masks"] +  "/" + dirs +  "/maskGT_" + filenumber + ".png"

                    if "estimate" in basepaths :
                        filename_dict["estimatepath"] = basepaths["estimate"]  + "/" + dirs + "/"
                        filename_dict["estflow"] = basepaths["estimate"] + "/" + dirs + "/frame_" + filenumber + ".flo"

                    filename_dict["filename"] = "frame_" + filenumber
                    filename_dict["dir"] = dirs
                    filename_dict["basepath"] = basepaths["basepath"]
                    self.filenames_dict.append(filename_dict)

"""
    create_filename_list(basepath) -> retval
    .   @brief Create a list of dictionaries containing file-paths for the optical flow dataset   
    .   @param basepath is a dictionary containing sub path. 
"""
def create_filename_list(basepath):
    fileparser = CrowdFileParser()
    fileparser.parseFilenames(basepath)
    return fileparser.filenames_dict