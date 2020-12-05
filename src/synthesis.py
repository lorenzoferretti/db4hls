import sys
import VivadoHLS
import itertools
import sweep_parser
import subprocess
import multiprocessing as mp
import hashlib


class Synthesiser:
    def __init__(self, synthesis_tool):
        self.synthesisTool = synthesis_tool
        self.projectName = None
        self.srcFolder = None
        self.srcFiles = None
        self.testBenchFile = None
        self.topFunction = None
        self.implementation = None
        self.tlcScript = None
        self.board = None
        self.explorationKnobs = None
        self.synthesisDstFolder = None
        self.synthesisScriptFolder = None
        self.synthesisZipFolder = None
        self.ID = 0

    def set_project(self, src_folder, src_files, test_bench_file, top_function, implementation,
                    dst_folder, script_folder, zip_folder):
        #self.projectName = project_name
        self.srcFolder = src_folder
        self.srcFiles = src_files
        self.testBenchFile = test_bench_file
        self.topFunction = top_function
        self.implementation = implementation
        self.synthesisDstFolder = dst_folder
        self.synthesisScriptFolder = script_folder
        self.synthesisZipFolder = zip_folder

    def set_board_specs(self, board):
        self.board = board

    def set_exploration_knobs(self, sweep_file):
        if self.synthesisTool == "vivado_hls":
            ds = sweep_parser.create_ds(sweep_file)
            self.explorationKnobs = ds
            pass
        else:
            print("Tool not supported")
            sys.exit()
        return ds

    def produce_directive_file_with_id(self, ds_object, config, identifier):
        knobs_type = ds_object["Knobs_type"]
        if len(knobs_type) != len(config):
            print("Configuration descriptor error")
            sys.exit()

        if self.synthesisTool == "vivado_hls":
            VivadoHLS.create_directive_script_with_id(self, ds_object, config, identifier)

    def produce_tcl_script_with_id(self, identifier):
        if self.synthesisTool == "vivado_hls":
            VivadoHLS.create_tcl_script_with_id(self, identifier)

    def explore(self, design_space, config, ds_exhaustive):
        depth = len(config)
        if depth == len(design_space):
            return
        else:
            feature_values = design_space[depth]
            feature_index = 0
            while feature_index < len(feature_values):
                feature = feature_values[feature_index]
                new_config = config + [feature]
                if len(new_config) == len(design_space):
                    self.produce_tcl_script_with_id(str(self.ID))
                    self.produce_directive_file_with_id(self.explorationKnobs, new_config, self.ID)
                    self.ID = self.ID + 1
                    ds_exhaustive.append(new_config)
                    feature_index = feature_index + 1
                else:
                    feature_index = feature_index + 1
                    self.explore(design_space, new_config, ds_exhaustive)

    def exhaustive_configs(self):
        ds_exhaustive = []
        kv = self.explorationKnobs["Knobs_values"]
        kb = self.explorationKnobs["Bindings"]
        self.explore_configs(kv, [], kb, [], ds_exhaustive)
        return ds_exhaustive

    def check_bind_condition(self, bind_config_info):
        bind = {}
        for b in bind_config_info:
            if b[0] is not None:
                if b[0] not in bind.keys():
                    bind[b[0]] = b[1]
                else:
                    if bind[b[0]] != b[1]:
                        return False

        return True

    def explore_configs(self, design_space, config, bindings, bind_configs, ds_exhaustive):
        depth = len(config)
        # identifier = 0
        if depth == len(design_space):
            return
        else:
            feature_values = design_space[depth]
            bind_values = bindings[depth]
            feature_index = 0
            while feature_index < len(feature_values):
                feature = feature_values[feature_index]
                bind = bind_values[feature_index]
                new_config = config + [feature]
                new_bind_configs = bind_configs + [bind]
                if len(new_config) == len(design_space):
                    if self.check_bind_condition(new_bind_configs):
                        ds_exhaustive.append(new_config)
                    feature_index = feature_index + 1
                else:
                    feature_index = feature_index + 1
                    self.explore_configs(design_space, new_config, bindings, new_bind_configs, ds_exhaustive)

    def synthesise_batch(self, configs, csd, n_cores, max_time):
        print("Starting batch...")
        hash_list = []
        config_set = set(map(tuple, configs))
        configs = list(map(list, config_set))
        for conf in configs:
            hash_object = hashlib.md5((str(conf) +
                                       str(self.topFunction)).encode())
            hash_id = hash_object.hexdigest()
            hash_list.append(hash_id)

        # invoke gnu parallel to generate all the script files
        print("Writing batch file...")
        batch_namelist_file = open(self.synthesisDstFolder + self.topFunction +
                                   "_" + self.implementation + "_batch.txt", "w+")
        for h in hash_list:
            batch_namelist_file.write(h+"\n")
        batch_namelist_file.close()

        print("Generating HSL scritps...")
        pool = mp.Pool(processes=int(n_cores))
        parallel_script_generation = [pool.apply(self.generates_scripts_from_configs, args=(h, c, csd))
                                      for h, c in zip(hash_list, configs)]

        print("Starting synthesis...")
        # Invoke gnu_parallel to run synthesis
        subprocess.call(["bash", "dse.sh", self.topFunction, self.implementation, str(max_time),
                         self.synthesisDstFolder, self.synthesisScriptFolder, self.synthesisZipFolder])

        return hash_list

    def generates_scripts_from_configs(self, h, c, csd):
        VivadoHLS.create_tcl_script_with_id(self, h)
        directive_script, knobs_to_add_to_db = VivadoHLS.create_directive_script_with_id(self, csd, c, h)
        return directive_script, knobs_to_add_to_db, c, h



