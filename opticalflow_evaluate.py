import file_parser as fp
import cv2
import sys
import pickle
import copy
import util as ut

def run_parameter(config_item):
    result = dict()
    result["ee"] = 0
    result["R1"] = 0
    result["R2"] = 0
    result["R3"] = 0
    result["no_points"] = 0
    # load ground truth optical flow
    flow_gt         = ut.readFlowFiles(config_item["files"]["gtflow"])
    # load ground truth mask indicating foreground and background flow vectors
    mask_rgb        = cv2.imread(config_item["files"]["mask"])
    #  load estimated optical flow
    est_flow = ut.readFlowFiles(config_item["files"]["estflow"])
    # compute short term errors
    result = ut.compute_error(est_flow, flow_gt, mask_rgb)

    return (config_item, result)


def main():
    if len(sys.argv) < 2:
        print("Please provide the first argument that is the root path of the CrowdFlow dataset.")
        return
    basepath = sys.argv[1]

    parameter_list = list()

    for n in range(2, len(sys.argv)):
        parameter_list.append({"flow_method": "/" + sys.argv[n]})

    latex_filename = "short_term_results.txt"
    result_filename = "short_term_results.pb"


    #basepath = "/data/Senst/AVSS2018/"
    #result_filename = "Short_Term_Results.pb"

    result_list = list()
    for parameter in parameter_list:
        basepath_dict = {"basepath": basepath,
                         "images" : basepath + "/images/",
                         "groundtruth": basepath + "/gt_flow/",
                         "estimate": basepath + "/estimate/" + parameter["flow_method"],
                         "masks": basepath + "/masks/",
                         }

        filenames = fp.create_filename_list(basepath_dict)
        config_list = ut.create_config(parameter, filenames)

        for config_item in config_list:
            result = run_parameter(config_item)
            result_list.append(copy.deepcopy(result))

    out_dict = {"result_list": result_list}
    print("Save short term evaluation file ",  result_filename)
    pickle.dump(out_dict, open( result_filename, "wb"))

    result_str = ut.getLatexTable(result_filename)
    print(result_str)
    if len(latex_filename) > 0:
        with open(latex_filename, "w") as f:
            f.write(result_str)
main()