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

    def create_vivadohls_ds(self, sweep_file):
        ds = {}
        with open(sweep_file) as f:
            content = f.readlines()

        f.close()
        content = [x.strip() for x in content]
        for c in content:
            if c is "":
                continue
            if "#" in c:
                continue
            if "@" in c:
                print("Binding knob values @a knobs")

            tmp = c.split(";")
            if tmp[0] not in VivadoHLS.hls_knobs:
                print(tmp[0] + " is not a valid knob")
            else:
                if tmp[0] in ds:
                    content = ds.get(tmp[0])
                    content.append(tmp[1:])
                    ds[tmp[0]] = content
                else:
                    ds[tmp[0]] = [tmp[1:]]
        design_space_knob_values = []
        design_space_knob_type = []
        design_space_knob = []
        disign_space_binding = {}
        for key in ds:
            values = ds.get(key)
            for i in range(len(values)):
                design_space_knob_type.append(key)
            for p in values:
                if key == "resource":
                    tmp = VivadoHLS.Resource(p[1], p[0])
                    design_space_knob.append(tmp)
                    tmp2 = p[-1]
                    tmp2 = tmp2.strip("{")
                    tmp2 = tmp2.strip("}")
                    tmp2 = tmp2.split(",")
                    design_space_knob_values.append(tmp2)
                if key == "unrolling":
                    tmp = VivadoHLS.Unrolling(p[1], p[0])
                    design_space_knob.append(tmp)
                    if "@" in p[-1]:
                        tmp2 = p[-1].split("@")
                        tmp4 = tmp2[1]
                        tmp2 = tmp2[0]
                    else:
                        tmp2 = p[-1]
                        tmp4 = None
                    #tmp2 = p[-1]
                    tmp2 = tmp2.strip("{")
                    tmp2 = tmp2.strip("}")
                    tmp2 = tmp2.split(",")
                    if tmp4 is None:
                        tmp5 = [(t,) for t in tmp2]
                        design_space_knob_values.append(tmp5)
                    else:
                        tmp5 = [(t, tmp4) for t in tmp2]
                        design_space_knob_values.append(tmp5)
                        #disign_space_binding[tmp4] = tmp5
                if key == "clock":
                    tmp = VivadoHLS.Clock(p[0])
                    design_space_knob.append(tmp)
                    tmp2 = p[-1]
                    tmp2 = tmp2.strip("{")
                    tmp2 = tmp2.strip("}")
                    tmp2 = tmp2.split(";")
                    design_space_knob_values.append(tmp2)
                if key == "array_partition":
                    tmp = VivadoHLS.Partition(p[1], p[0], p[2])
                    design_space_knob.append(tmp)
                    if "@" in p[-1]:
                        tmp2 = p[-1].split("@")
                        tmp4 = tmp2[1]
                        tmp2 = tmp2[0]
                    else:
                        tmp4 = None
                        tmp2 = p[-1]
                    #tmp2 = p[-1]
                    tmp2 = tmp2.strip("{")
                    tmp2 = tmp2.strip("}")
                    tmp2 = tmp2.split(",")
                    tmp3 = p[-2]
                    tmp3 = tmp3.strip("{")
                    tmp3 = tmp3.strip("}")
                    tmp3 = tmp3.split(",")
                    if "complete" in tmp3:
                        tmp3.remove("complete")
                        if tmp4 is None:
                            k_values_tmp = [item for item in itertools.product((tmp2,), tmp3)]
                        else:
                            k_values_tmp = [item for item in itertools.product((tmp2, tmp4), tmp3)]
                        k_values_tmp.append("complete")
                    else:
                        if tmp4 is None:
                            tmp5 = [(t,) for t in tmp2]
                            k_values_tmp = [item for item in itertools.product(tmp5, tmp3)]
                        else:
                            tmp5 = [(t, tmp4) for t in tmp2]
                            k_values_tmp = [item for item in itertools.product(tmp5, tmp3)]
                            #disign_space_binding[tmp4] = tmp5
                        #k_values_tmp = [item for item in itertools.product(tmp2, tmp3)]
                    design_space_knob_values.append(k_values_tmp)

                if key == "inlining":
                    tmp = VivadoHLS.Inlining(p[0])
                    design_space_knob.append(tmp)
                    tmp = p[-1]
                    tmp = tmp.strip("{")
                    tmp = tmp.strip("}")
                    tmp = tmp.split(",")
                    design_space_knob_values.append(tmp)

        ds_obj = {
            "DS": ds,
            "Knobs_values": design_space_knob_values,
            "Knobs_type": design_space_knob_type,
            "Knobs": design_space_knob,
            "Bindings": disign_space_binding
        }

        # print(ds_obj)
        self.explorationKnobs = ds_obj
        return ds_obj

    def set_exploration_knobs(self, sweep_file):
        if self.synthesisTool == "vivado_hls":
            ds = sweep_parser.create_ds(sweep_file)
            self.explorationKnobs = ds
            #ds = self.create_vivadohls_ds(sweep_file)
            # for knob in explorationKnobs:
            # 	if knob[1] not in VivadoHLS.knobs:
            # 		print "The tool does not support \"" + knob + "\" directives"
            # 		sys.exit()
            pass
        else:
            print("Tool not supported")
            sys.exit()

        return ds

    # self.explorationKnobs = explorationKnobs
    # self.create_VivadoHLS_ds(sweepFile)

    def produce_directive_file(self, ds_object, config):
        # knobs_values = ds_object["Knobs_values"]
        knobs_type = ds_object["Knobs_type"]
        # knobs = ds_object["Knobs"]
        if len(knobs_type) != len(config):
            print("Configuration descriptor error")
            sys.exit()

        if self.synthesisTool == "vivado_hls":
            VivadoHLS.createDirectiveScritp(self, ds_object, config)

    def produce_directive_file_with_id(self, ds_object, config, identifier):
        # knobs_values = ds_object["Knobs_values"]
        knobs_type = ds_object["Knobs_type"]
        # knobs = ds_object["Knobs"]
        if len(knobs_type) != len(config):
            print("Configuration descriptor error")
            sys.exit()

        if self.synthesisTool == "vivado_hls":
            VivadoHLS.create_directive_script_with_id(self, ds_object, config, identifier)

    def produce_tcl_script(self):
        if self.synthesisTool == "vivado_hls":
            VivadoHLS.createTclScritp(self)

    def produce_tcl_script_with_id(self, identifier):
        if self.synthesisTool == "vivado_hls":
            VivadoHLS.create_tcl_script_with_id(self, identifier)

    def start_new_exploration(self):
        ds_exhaustive = []
        kv = self.explorationKnobs["Knobs_values"]
        self.explore(kv, [], ds_exhaustive)
        return ds_exhaustive

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
                    #print("----" * 10)
                    #print(self.explorationKnobs)
                    #print(new_config)
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
                #print("Feature_index: ", str(feature_index))
                if len(new_config) == len(design_space):
                    if self.check_bind_condition(new_bind_configs):
                        ds_exhaustive.append(new_config)
                    feature_index = feature_index + 1
                else:
                    feature_index = feature_index + 1
                    self.explore_configs(design_space, new_config, bindings, new_bind_configs, ds_exhaustive)

    def create_synthesis_tool_invocation_script(self):
        if self.synthesisTool == "vivado_hls":
            f = open(self.synthesisDstFolder + "invokeVivadoHLS.sh", "w")
            # content = "source /tools2/Xilinx/Vivado/2018.3/settings64.sh\n"
            content = "vivado_hls -f " + self.topFunction + ".tcl\n"
            f.write(content)
            f.close()

    def create_synthesis_tool_invocation_script_with_id(self, identifier):
        if self.synthesisTool == "vivado_hls":
            f = open(self.synthesisDstFolder + "invokeVivadoHLS_" + identifier + ".sh", "w")
            content = "vivado_hls -f " + self.topFunction + "_" + identifier + ".tcl\n"
            f.write(content)
            f.close()

    def synthesise_batch(self, configs, csd, n_cores, max_time):
        print("Starting batch...")
        hash_list = []
        id_list = []
        discretized_configs = []
        # Check if configuration have already been synthesised remove the one already synthesised
        config_set = set(map(tuple, configs))
        configs = list(map(list, config_set))
        for conf in configs:
            # disc_conf = self.lattice.revert_discretized_config(conf)
            # discretized_configs.append(disc_conf)
            hash_object = hashlib.md5((str(conf) +
                                       str(self.topFunction)).encode())
            hash_id = hash_object.hexdigest()
            hash_list.append(hash_id)
        # db = db_info["db"]
        # db.connect_to_db()
        # n_core = db.get_machine_core_n(db_info["machine_id"])
        # db.close_connection()

        #print(n_core)
        # Discretize conf
        # discretized_configs = [pool.apply(self.parallel_discretize_conf, args=(c,))
        #                               for c in configs]
        # Generate hashes
        # hash_list = [pool.apply(self.parallel_generate_hashes, args=(c, db_info["ds_id"]))
        #                               for c in discretized_configs]


        # invoke gnu parallel to generate all the script files
        print("Writing batch file...")
        batch_namelist_file = open(self.synthesisDstFolder + self.topFunction +
                                   "_" + self.implementation + "_batch.txt", "w+")
        # print("Adding configurations to db...")
        # db.connect_to_db()
        for h in hash_list:
            batch_namelist_file.write(h+"\n")
            # hash_id = db.add_dse_configuration(db_info["ds_id"], h)
            # id_list.append(h)
        # db.close_connection()
        batch_namelist_file.close()

        print("Generating HSL scritps...")
        pool = mp.Pool(processes=int(n_cores))
        parallel_script_generation = [pool.apply(self.generates_scripts_from_configs, args=(h, c, csd))
                                      for h, c in zip(hash_list, configs)]

        # print("Adding knobs to database...")
        # db.connect_to_db()
        # for result in parallel_script_generation:
        #     #print(result)
        #     ds_script = result[0]
        #     id_conf = result[3]
        #     config = result[2]
        #     knobs = result[1]
        #     for i in range(0,len(config)):
        #         id_knob = db.add_knob(knobs[i][0], knobs[i][1])
        #         db.add_knob_to_dse_configuration(id_conf, id_knob)
        #         # TODO add JSON descriptor
        #     db.add_directive_script_to_dse_configuration(id_conf, ds_script, config)
        # db.close_connection()

        # for result in parallel_script_generation:
        #     # print(result)
        #     ds_script = result[0]
        #     id_conf = result[3]
        #     config = result[2]
        #     knobs = result[1]
        #     for i in range(0, len(config)):
        #         knob_string = knobs[i][0] + "-" + knobs[i][1]
        #         if knob_string in self.local_knob_table.keys():
        #             id_knob = self.local_knob_table[knob_string]
        #         else:
        #             # id_knob = db.add_knob(knobs[i][0], knobs[i][1])
        #             self.local_knob_table[knob_string] = id_knob
        #         # db.add_knob_to_dse_configuration(id_conf, id_knob)
        #         # TODO add JSON descriptor
        #     # db.add_directive_script_to_dse_configuration(id_conf, ds_script, config)
        # # db.close_connection()
        # #print(results)
        # #processes = [mp.Process(target=self.generates_scripts_from_configs,
        # #                        args=(id_list, discretized_configs, db_info, db, ds)) for x in range(8)]

        # Run processes
        #for p in processes:
        #    p.start()
        #
        # for h, c in zip(hash_list, discretized_configs):
        #     hash_id = db.add_dse_configuration(db_info["ds_id"], h)
        #     id_list.append(hash_id)
        #     VivadoHLS.create_tcl_script_with_id(self.synthesis_info, hash_id)
        #     directive_script = VivadoHLS.create_directive_script_with_id(self.synthesis_info, ds, c, hash_id,
        #                                                                  db, db_info)
        #     db.add_directive_script_to_dse_configuration(hash_id, directive_script, c)
        #
        # db.close_connection()

        print("Starting synthesis...")
        # Invoke gnu_parallel to run synthesis
        subprocess.call(["bash", "dse.sh", self.topFunction, self.implementation, str(max_time),
                         self.synthesisDstFolder, self.synthesisScriptFolder, self.synthesisZipFolder])

        return hash_list

    def generates_scripts_from_configs(self, h, c, csd):
        # for h, c in zip(id_list, discretized_configs):
        VivadoHLS.create_tcl_script_with_id(self, h)
        # db.close_connection()
        directive_script, knobs_to_add_to_db = VivadoHLS.create_directive_script_with_id(self, csd, c, h)
        # db.add_directive_script_to_dse_configuration(h, directive_script, c)
        # db.close_connection()
        return directive_script, knobs_to_add_to_db, c, h



