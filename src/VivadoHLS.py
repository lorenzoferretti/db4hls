import sys

hls_knobs = ['clock', 'array_partition', 'resource', 'pipeline', 'unroll', 'bundling', 'inline']


def create_directive_script_with_id(synthesis_info, ds_object, config, identifier, db, db_info):
    script = ""
    # directive_file = open(
    #     synthesis_info.synthesisDstFolder + synthesis_info.topFunction + "_" + str(identifier) + ".dir", "w+")

    directive_file = open(synthesis_info.synthesisScriptFolder + str(identifier) + ".dir", "w+")

    knobs_values = ds_object["Knobs_values"]
    knobs_type = ds_object["Knobs_type"]
    knobs = ds_object["Knobs"]
    #print(config)
    add_to_db = []
    for k, c, kv, kt in zip(knobs, config, knobs_values, knobs_type):
        pragma_str, knob_to_add_to_db = generate_pragma(knob=k, config=c, knob_value=kv, knob_type=kt,
                                                        db=db, id_conf=identifier)
        script += pragma_str
        add_to_db.append(knob_to_add_to_db)

    if len(config) < len(knobs_values):
        for k, kv, kt in zip(knobs, knobs_values, knobs_type):
            if len(kv) == 1:
                pragma_str, knob_to_add_to_db = generate_pragma(knob=k, config=None, knob_value=kv, knob_type=kt,
                                                                db=db, id_conf=identifier)
                script += pragma_str
                add_to_db.append(knob_to_add_to_db)

    directive_file.write(script)
    directive_file.close()
    return script, add_to_db


def create_directive_script(synthesis_info, ds_object, config):
    script = ""
    directive_file = open(synthesis_info.topFunction + ".dir", "w+")

    knobs_values = ds_object["Knobs_values"]
    knobs_type = ds_object["Knobs_type"]
    knobs = ds_object["Knobs"]
    for k, c, kv, kt in zip(knobs, config, knobs_values, knobs_type):
        script += generate_pragma(knob=k, config=c, knob_value=kv, knob_type=kt)

    if len(config) < len(knobs_values):
        for k, kv, kt in zip(knobs, knobs_values, knobs_type):
            if len(kv) == 1:
                script += generate_pragma(knob=k, config=None, knob_value=kv, knob_type=kt)

    directive_file.write(script)
    directive_file.close()


def generate_pragma(knob, config, knob_value, knob_type, db, id_conf):
    knob_to_add_to_db = None
    # TODO ADD LOCATION TO KNOB
    if knob_type == "resource":
        if config is None:
            knob.set_type(knob_value)
            knob_to_add_to_db = (knob_type, knob_value)
            # id_knob = db.add_knob(knob_type, knob_value)
        else:
            knob.set_type(config)
            knob_to_add_to_db = (knob_type, config)
            # id_knob = db.add_knob(knob_type, config)

        # db.add_knob_to_dse_configuration(id_conf, id_knob)
        return knob.print_pragma(), knob_to_add_to_db

    if knob_type == "unroll":
        if config is None:
            knob.set_factor(knob_value)
            # id_knob = db.add_knob(knob_type, knob_value)
            knob_to_add_to_db = (knob_type, knob_value)
        else:
            knob.set_factor(config)
            # id_knob = db.add_knob(knob_type, config)
            knob_to_add_to_db = (knob_type, config)

        # db.add_knob_to_dse_configuration(id_conf, id_knob)
        return knob.print_pragma(), knob_to_add_to_db

    if knob_type == "clock":
        if config is None:
            knob.set_clock_period_ns(knob_value)
            knob_to_add_to_db = (knob_type, knob_value)
        else:
            knob.set_clock_period_ns(config)
            knob_to_add_to_db = (knob_type, config)
        return knob.print_frequency(), knob_to_add_to_db

    if knob_type == "array_partition":
        if config is None:
            if type(knob_value) is tuple:
                knob.set_type(knob_value[0])
                knob.set_factor(knob_value[1])
                knob_to_add_to_db = (knob_type, "" + knob_value[0] + "," + knob_value[1])
                # id_knob = db.add_knob(knob_type, "" + knob_value[1] + "," + knob_value[0])
            else:
                knob.set_type(knob_value)
                knob_to_add_to_db = (knob_type, knob_value)
                # id_knob = db.add_knob(knob_type, knob_value)

        else:
            if type(config) is tuple and config[1] is not None:
                #print(config)
                knob.set_type(config[0])
                knob.set_factor(config[1])
                # id_knob = db.add_knob(knob_type, ""+config[1]+","+config[0])
                knob_to_add_to_db = (knob_type, "" + config[0] + "," + config[1])
            else:
                knob.set_type(config)
                # print(config)
                # print(knob_type)
                knob_to_add_to_db = (knob_type, config[0])
                # id_knob = db.add_knob(knob_type, config)

        # db.add_knob_to_dse_configuration(id_conf, id_knob)
        return knob.print_pragma(), knob_to_add_to_db

    if knob_type == "inline":
        if config is None:
            knob.set_inline(knob_value)
            # print(type(knob_type))
            # print(knob_value)
            knob_to_add_to_db = (knob_type, "" + knob_value[0])
            #id_knob = db.add_knob(knob_type, "" + knob_value[0])
        else:
            knob.set_inline(config)
            knob_to_add_to_db = (knob_type, config)
            # id_knob = db.add_knob(knob_type, config)
        # TODO evaluate options
        # id_knob = db.add_knob(knob_type, config)
        # db.add_knob_to_dse_configuration(id_conf, id_knob)
        return knob.print_pragma(), knob_to_add_to_db

    return None, knob_to_add_to_db


def create_tcl_script(synthesis_info):
    script = ""
    tcl_file = open(synthesis_info.synthesisDstFolder + synthesis_info.topFunction + ".tcl", "w+")

    script += "proc report_time { op_name time_start time_end } {\n"
    script += "  set time_taken [expr $time_end - $time_start]\n"
    script += "  set time_s [expr ($time_taken / 1000) % 60]\n"
    script += "  set time_m [expr ($time_taken / (1000*60)) % 60]\n"
    script += "  set time_h [expr ($time_taken / (1000*60*60)) % 24]\n"
    script += "  puts \"***** ${op_name} COMPLETED IN ${time_h}h${time_m}m${time_s}s *****\"\n"
    script += "}\n"

    script += "\n"

    script += "open_project " + synthesis_info.projectName + "\n"

    script += "\n"

    script += "set_top " + synthesis_info.topFunction + "\n"

    script += "\n"

    for f in synthesis_info.srcFiles:
        script += "add_files " + synthesis_info.srcFolder + f + "\n"

    if synthesis_info.testBenchFile != "":
        script += "add_files -tb " + synthesis_info.srcFolder + synthesis_info.testBenchFile + "\n"

    script += "\n"

    script += "open_solution -reset \"solution\"" + "\n"
    script += "set_part " + synthesis_info.board + "\n"

    script += "\n"

    script += "source ./" + synthesis_info.topFunction + ".dir" + "\n"

    script += "\n"

    script += "set time_start [clock clicks -milliseconds]\n"

    script += "\n"

    script += "csynth_design" + "\n"

    script += "\n"

    script += "set time_end [clock clicks -milliseconds]\n"

    script += "\n"

    script += "report_time \"C/RTL SYNTHESIS\" $time_start $time_end\n"

    script += "\n"

    script += "exit"

    tcl_file.write(script)
    tcl_file.close()


def create_tcl_script_with_id(synthesis_info, identifier):
    script = ""
    # tcl_file = open(synthesis_info.synthesisDstFolder + synthesis_info.topFunction + "_" + str(identifier) + ".tcl",
    #                 "w+")

    tcl_file = open(synthesis_info.synthesisScriptFolder + str(identifier) + ".tcl", "w+")

    script += "proc report_time { op_name time_start time_end } {\n"
    script += "  set time_taken [expr $time_end - $time_start]\n"
    script += "  set time_s [expr ($time_taken / 1000) % 60]\n"
    script += "  set time_m [expr ($time_taken / (1000*60)) % 60]\n"
    script += "  set time_h [expr ($time_taken / (1000*60*60)) % 24]\n"
    script += "  puts \"***** ${op_name} COMPLETED IN ${time_h}h${time_m}m${time_s}s *****\"\n"
    script += "}\n"

    script += "\n"

    script += "open_project " + synthesis_info.topFunction + "-" + \
              synthesis_info.implementation + "-" + str(identifier) + "\n"

    script += "\n"

    script += "set_top " + synthesis_info.topFunction + "\n"

    script += "\n"

    for f in synthesis_info.srcFiles:
        script += "add_files " + synthesis_info.srcFolder + f + "\n"

    script += "add_files -tb " + synthesis_info.srcFolder + synthesis_info.testBenchFile + "\n"

    # for filename in os.listdir(synth_info.srcFolder):
    #       if filename.endswith(".c") or filename.endswith(".h") or filename.endswith(".data"):
    #               if filename != synth_info.testBenchFile:
    #                       script += "add_files " + filename + "\n"
    #               else:
    #                       script += "add_files -tb " + filename + "\n"

    #       else:
    #               continue

    script += "\n"

    script += "open_solution -reset \"solution\"" + "\n"
    script += "set_part " + synthesis_info.board + "\n"

    script += "\n"

    script += "source " + synthesis_info.synthesisScriptFolder + str(identifier) + ".dir" + "\n"

    #        script += "\n"

    #        script += "csim_design -clean" + "\n"

    script += "\n"

    script += "set time_start [clock clicks -milliseconds]\n"

    script += "\n"

    script += "csynth_design" + "\n"

    script += "\n"

    script += "set time_end [clock clicks -milliseconds]\n"

    script += "\n"

    script += "report_time \"C/RTL SYNTHESIS\" $time_start $time_end\n"

    script += "\n"

    script += "exit"

    tcl_file.write(script)
    tcl_file.close()


class Resource:
    def __init__(self, label, function):
        self.resourceType = None
        self.targetLabel = label
        self.targetFunction = function

    def set_type(self, res_type):
        self.resourceType = res_type

    def print_pragma(self):
        return "set_directive_resource -core " + self.resourceType + " \"" + self.targetFunction + "\" " + \
               self.targetLabel + "\n"


class Partition:
    def __init__(self, label, function, dim):
        self.dimension = dim
        self.factor = None
        self.partType = None
        self.targetFunction = function
        self.targetLabel = label
        self.acceptableTypes = ["cyclic", "complete", "block"]

    def set_type(self, part_type):
        self.partType = part_type

    def set_factor(self, part_factor):
        self.factor = part_factor

    def print_pragma(self):
        #print("Part type: "+self.partType)
        if self.partType == "complete" and self.factor is None:
            return "set_directive_array_partition -type " + self.partType + " -dim " + \
                                   self.dimension + " \"" + self.targetFunction + "\" " + self.targetLabel + "\n"

            #print("SONO UGUALE")
        #print("Part factor: "+str(self.factor))    
        if self.dimension is None:
            print("Partitioning target dimension not defined")
            sys.exit()
        else:
            if int(self.dimension) < 0:
                print("Partitioning target dimension must be greater than 0")
                sys.exit()

        if self.factor is None and self.partType != "complete":
            print("Partitioning factor not defined")
            sys.exit()
        else:
            if int(self.factor) < 0 and self.partType != "complete":
                print("Partitioning factor must be greater than 0")
                sys.exit()

        if self.partType is None:
            print("Partitioning type not defined")
            sys.exit()
        else:
            if self.partType not in self.acceptableTypes:
                print("Partitioning type can be one of these type: " + str(self.acceptableTypes))
                sys.exit()

        return "set_directive_array_partition -type " + self.partType + " -factor " + self.factor + " -dim " + \
               self.dimension + " \"" + self.targetFunction + "\" " + self.targetLabel + "\n"


class Clock:
    def __init__(self,):
        self.clockPeriod = None
        self.targetLabel = "clock"

    def set_clock_period_ns(self, period):
        self.clockPeriod = period

    def set_frequency_mhz(self, frequency):
        self.clockPeriod = 1. / float(frequency) * (10 ^ 3)

    def print_frequency(self):
        if self.clockPeriod is None:
            print("Clock period must be defined")
            sys.exit()

        if int(self.clockPeriod) < 0:
            print("Clock period must be greater than 0")
            sys.exit()

        return "create_clock -period " + str(self.clockPeriod)


class Unrolling:
    def __init__(self, label, function):
        self.targetLabel = label
        self.targetFunction = function
        self.factor = None

    def set_factor(self, factor):
        self.factor = factor

    def print_pragma(self):
        if self.factor is None:
            print("Unrolling factor must be defined")
            sys.exit()

        if int(self.factor) < 0:
            print("Unrolling factor must be greater than 0")
            sys.exit()

        return "set_directive_unroll -factor " + str(
            self.factor) + " \"" + self.targetFunction + "/" + self.targetLabel + "\"\n"


class Inlining:
    def __init__(self, label):
        self.targetLabel = label
        self.enabled = None
        self.region = None
        self.recursive = None

    def set_inline(self, value):
        if value.lower() == "off":
            self.enabled = "off"
        if value.lower() == "on":
            self.enabled = "on"

    def set_region(self, region):
        self.region = region

    def set_recursive(self, recursive):
        self.recursive = recursive

    def print_pragma(self):
        pragma = "set_directive_inline"
        if self.enabled == "off":
            pragma += " -off"
        if self.region is not None:
            pragma += " -region"
        if self.recursive is not None:
            pragma += " -recursive"
        pragma += " " + self.targetLabel + "\n"
        return pragma
