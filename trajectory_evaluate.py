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
import copy
import time
import sys
import numpy as np
import pickle
import util as ut
import file_parser as fp


class Trajectory:
    def __init__(self, pos, from_idx, to_idx):
        self.points = np.ones(shape=(int(to_idx) - int(from_idx) + 1, 2), dtype=np.float32) * 99999
        self.points[0,:] = pos
        self.start_index = int(from_idx)

    def run(self, flow, index):
        idx = index - self.start_index
        if idx >= 0 and idx + 1 < self.points.shape[0]:
            # position is in (x,y)
            pos = self.points[idx,:]
            ipos = np.floor(pos).astype(np.int32)
            if ipos[0] >= 0 and ipos[1] >= 0 and ipos[0] + 1 < flow.shape[1] and ipos[1] + 1 < flow.shape[0]:
                a = pos - ipos
                iw00 = (1 - a[0]) * (1 - a[1])
                iw01 = a[0] * (1 - a[1])
                iw10 = (1 - a[0]) * a[1]
                iw11 = 1 - iw00 - iw01 - iw10
                self.points[idx + 1, :] = pos + \
                    flow[ipos[1], ipos[0]] * iw00 + \
                    flow[ipos[1], ipos[0] + 1] * iw01 + \
                    flow[ipos[1] + 1, ipos[0]] * iw10 + \
                    flow[ipos[1] + 1, ipos[0] + 1] * iw11

class TrajectoryEvaluator:
    def __init__(self,
                 thresholds=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                 dense_person_groundtruth_filename_base="DenseTracks.pb",
                 person_groundtruth_filename="PersonTracks.pb"):
        self.dense_person_groundtruth_filename_base = None
        self.person_groundtruth_filename = None

        if dense_person_groundtruth_filename_base is not None:
            self.dense_person_groundtruth_filename_base = copy.deepcopy(dense_person_groundtruth_filename_base)
        if person_groundtruth_filename is not None:
            self.person_groundtruth_filename = copy.deepcopy(person_groundtruth_filename)

        self.threshold_list = copy.deepcopy(thresholds)

    def compute_differenz_trajectories(self, flow_filenames, groundtruth_filename):
        print(" Load ", groundtruth_filename)
        ret = pickle.load(open(groundtruth_filename, "rb"))
        start_points_trajectory = ret["GT_StartPoints"]
        gt_trajectory = ret["GT_Trajectories"]
        print(" Start TrajectoryEstimator ", flow_filenames[0])

        trajectory_list = list()
        for r in range(0,start_points_trajectory.shape[0]):
            trajectory_list.append(Trajectory(pos = (start_points_trajectory[r,3], start_points_trajectory[r,2]) ,
                                         from_idx = start_points_trajectory[r,0], to_idx= start_points_trajectory[r,1]))

        for i, flow_file in enumerate(flow_filenames):
            flow = ut.readFlowFiles(flow_file)
            for trajectory_item in trajectory_list:
                trajectory_item.run(flow, i)

        estimated_trajectory = list()
        for trajectory_item in trajectory_list:
            estimated_trajectory.append(list())
            for n in range(trajectory_item.points.shape[0]):
                estimated_trajectory[-1].append(trajectory_item.points[n,1])
                estimated_trajectory[-1].append(trajectory_item.points[n,0])

        return ut.differenz_trajectory_list(gt_trajectory, estimated_trajectory)

    def run_sequence(self, sequence_name):
        start = time.time()
        print("Start ", sequence_name)
        flow_filenames = list()
        filebase = None
        for f in self.file_dict:
            if f["dir"] == sequence_name:
                filebase = f["basepath"]

                flow_filenames.append(f["estflow"])

        flow_filenames = sorted(flow_filenames)
        result = dict()
        gt_filebase = filebase + "/gt_trajectories/" + sequence_name + "/"
        if self.person_groundtruth_filename is not None:
            person_diff_trajectory = self.compute_differenz_trajectories(flow_filenames,
                                                                         gt_filebase + self.person_groundtruth_filename)
            result["person"] = ut.compute_tracking_error(person_diff_trajectory, self.threshold_list)
            print("Done  person_groundtruth_filename ")

        if self.dense_person_groundtruth_filename_base is not None:
            print("Start next")
            dense_person_diff_trajectory = self.compute_differenz_trajectories(flow_filenames,
                                                                               gt_filebase + self.dense_person_groundtruth_filename_base)
            result["dense_person"] = ut.compute_tracking_error(dense_person_diff_trajectory, self.threshold_list)
            print("Done  dense_person_groundtruth_filename_base ")

        print(time.time() - start)
        return result

    def average(self, sequences):
        keys = []
        if self.dense_person_groundtruth_filename_base is not None:
            keys.append("dense_person")
        if self.person_groundtruth_filename is not None:
            keys.append("person")
        result = dict()
        no_sequences = 1.0 / len(sequences)
        for seq_key in sequences.keys():
            for key in keys:
                if key in result:
                    result[key] = result[key] + np.array(sequences[seq_key][key]) * no_sequences
                else:
                    result[key] = np.array(sequences[seq_key][key]) * no_sequences

        return result

    def run(self, file_dict):
        self.file_dict = copy.deepcopy(file_dict)
        result = dict()

        sequence_name = ["IM01", "IM02", "IM03", "IM04", "IM05"]
        static_ret = dict()
        for s in sequence_name:
            static_ret[s] = self.run_sequence(s)
        result["static"] = self.average(static_ret)
        result = {**result, **static_ret}

        sequence_name = ["IM01_hDyn", "IM02_hDyn", "IM03_hDyn", "IM04_hDyn", "IM05_hDyn"]
        dynamic_ret = dict()
        for s in sequence_name:
            dynamic_ret[s] = self.run_sequence(s)
        result["dynamic"] = self.average(dynamic_ret)
        result = {**result, **dynamic_ret}
        result["all"] = self.average({**dynamic_ret, **static_ret})
        return result

    def get_statistics(self, basepath):
        static_sequence_name = ["IM01", "IM02", "IM03", "IM04", "IM05"]
        dynamic_sequence_name = ["IM01_hDyn", "IM02_hDyn", "IM03_hDyn", "IM04_hDyn", "IM05_hDyn"]
        sequence_name = static_sequence_name + dynamic_sequence_name

        length_list = list()
        for seq in sequence_name:
            filename_base = basepath + "/gt_trajectories/" + seq + "/"
            ret = pickle.load(open(filename_base + self.person_groundtruth_filename, "rb"))
            retl = ut.get_trajectory_lengths(ret["GT_Trajectories"])
            length_list = length_list + retl

        print("Max Length", np.max(length_list))
        np.save("Person_Trajectory_Length", np.array(length_list))
        print("Done Stored")

def run_parameter(flow_method, basepath):

      basepath_dict = {"basepath": basepath,
                         "images" : basepath + "/images/",
                         "groundtruth": basepath + "/gt_flow/",
                         "estimate": basepath + "/estimate/" + flow_method + "/",
                         "masks": basepath + "/masks/",
                         }

      filenames = fp.create_filename_list(basepath_dict)
      evaluator = TrajectoryEvaluator()
      ret_dict = evaluator.run(filenames)
      ret_dict["name"]  = flow_method.replace("/", "")
      return ret_dict


def main():
    if len(sys.argv) < 2:
        print("Please provide the first argument. Root path of the CrowdFlow dataset.")
        return
    basepath = sys.argv[1]

    method_list = list()
    for n in range(2, len(sys.argv)):
        method_list.append("/" + sys.argv[n] + "/" )

    latex_filename = "long_term_results.tex"
    result_filename = "long_term_results.pb"



    result_dict = list()

    for method in method_list:
        result_dict.append(run_parameter(method, basepath))

    print("Try to save file ",  result_filename)
    pickle.dump(result_dict, open( result_filename, "wb"))
    print("Person Trajectories")
    result_str = ut.genTrajectoryLatexTable(filename=result_filename, item_key="dense_person")
    print("Dense Person Trajectories")
    result_str = result_str + ut.genTrajectoryLatexTable(filename=result_filename, item_key="person")
    if len(latex_filename) > 0:
        with open(latex_filename, "w") as f:
            f.write(result_str)

main()
