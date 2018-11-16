import copy
import time
import sys
import numpy as np
import pickle
import util as ut
import file_parser as fp
import trajectory_evaluation as te


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
        import pytrajectory
        print(" Load ", groundtruth_filename)
        ret = pickle.load(open(groundtruth_filename, "rb"))
        start_points_trajectory = ret["GT_StartPoints"]
        gt_trajectory = ret["GT_Trajectories"]
        print(" Start TrajectoryEstimator ", flow_filenames[0])
        proc = pytrajectory.TrajectoryEstimator()
        estimated_trajectory = proc.run(flow_filenames, start_points_trajectory, 0, 0)  # 1.05)

        return ut.differenz_trajectory_list(gt_trajectory, estimated_trajectory)

    def run_sequence(self, sequence_name):
        start = time.time()
        print("Start ", sequence_name)
        flow_filenames = list()
        filebase = None
        for f in self.file_dict:
            if f["dir"] == sequence_name:
                filebase = f["basepath"]

                flow_filenames.append(f["estflow"] + f["filename"] + ".flo")

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
        return {file_dict[0]["estimatepath"]: result}

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
                        "estimate": basepath + "/estimate/" + flow_method + "/",
                        "images": basepath + "/images/",
                       }
      train_filenames, valid_filenames = fp.create_filename_list(basepath_dict)
      filenames = train_filenames + valid_filenames
      evaluator = te.TrajectoryEvaluator()
      ret_dict = evaluator.run(filenames)
      return ret_dict


def main():
    if len(sys.argv) < 2:
        print("Please provide the first argument. Root path of the CrowdFlow dataset.")
        return

    if len(sys.argv) < 3:
        print("Please provide the second argument. Directory name containing .")
        return

    if len(sys.argv) < 3:
        latex_filename = "long_term_results.txt"
    else:
        latex_filename = sys.argv[2]

    if len(sys.argv) < 4:
        result_filename = "long_term_results.pb"
    else:
        result_filename = sys.argv[3]
    basepath = sys.argv[1]
    result_filename = "long_term_results.pb"
    method_list = list()
    method_list.append( "/dual")
    result_dict = list()


    for method in method_list:
        result_dict.append(run_parameter(method, basepath))

    print("Try to save file ",  result_filename)
    pickle.dump(result_dict, open( result_filename, "wb"))
    print("Person Trajectories")
    ut.genTrajectoryLatexTable(filename=result_filename, item_key="dense_person")
    print("Dense Person Trajectories")
    ut.genTrajectoryLatexTable(filename=result_filename, item_key="person")

main()
