import sys
import VivadoHLS
import itertools
import math


def integer_divisors(start, end, none):
    divs = [1]
    for i in range(2, int(math.sqrt(int(end)))+1):
        if int(end) % i == 0:
            divs.extend([i, int(int(end)/i)])
    divs.extend([int(end)])
    divisors = list(set(divs))
    divisors.sort()
    divisors = [str(i) for i in divisors]
    to_return = []
    for i in range(len(divisors)):
        if int(start) <= int(divisors[i]) <= int(end):
            to_return.append(divisors[i])
    return to_return


def pow_n(start, end, power):
    iterations = int(math.log(int(end), int(power)))+1
    powers = [str(int(math.pow(int(power), i))) for i in range(iterations)]
    if start < powers[0]:
        powers = [start] + powers
    if end != powers[-1]:
        powers.append(end)
    return powers


def step_n(start, end, step):
    i = int(start)
    e = int(end)
    to_return = []
    while i <= e:
        to_return.append(str(i))
        i = i + int(step)
    to_return.append(end)
    return to_return


def parse_knob_literal_values(knob_values):
    tmp = knob_values.split("@")
    if tmp[0][0] != "{" or tmp[0][-1] != "}":
        print("Wrong input format. Knob values format: '{v1, v2, ..., v3}'")
        sys.exit()
    if len(tmp) > 1:
        binding = tmp[1]
    else:
        binding = None
    # if knob_values[0] != "{" or knob_values[-1] != "}":
    #     print("Wrong input format. Knob values format: '{v1, v2, ..., v3}'")
    #     print(knob_values)
    #     sys.exit()
    # tmp = knob_values.split("@")
    # if len(tmp) > 1:
    #     binding = tmp[1]
    # else:
    #     binding = None
    knob_values = tmp[0].strip("{")
    knob_values = knob_values.strip("}")
    knob_values = knob_values.split(",")

    return knob_values, binding


def parse_knob_digit_values(knob_values):
    accepted_functions ={"integer_divisors": integer_divisors, "step_": step_n, "pow_": pow_n}
    bind = [pos for pos, char in enumerate(knob_values) if char == "@"]
    if len(bind) == 0:
        if knob_values[0] != "{" or knob_values[-1] != "}":
            print("Wrong input format. Knob values format: '{v1, v2, ..., v3}' or '{v1->v2,step_func}'")
            print(knob_values)
            sys.exit()
    else:
        if knob_values[0] != "{" or knob_values[bind[0]-1] != "}":
            print("Wrong input format. Knob values format: '{v1, v2, ..., v3}' or '{v1->v2,step_func}'")
            print(knob_values)
            sys.exit()
    tmp = knob_values.split("@")
    if len(tmp) > 1:
        binding = tmp[1]
    else:
        binding = None

    tmp1 = tmp[0].strip("{")
    tmp1 = tmp1.strip("}")
    tmp1 = tmp1.split(",")
    if len(tmp1) == 2 and "->" in tmp1[0]:
        lht = tmp1[0]
        rht = tmp1[1]
        lht_values = lht.split("->")
        start = lht_values[0]
        end = lht_values[1]
        dictionary_keys = [key for key in accepted_functions.keys()]
        rht_func = None
        for i in range(len(dictionary_keys)):
            key = dictionary_keys[i]
            if key == rht:
                rht_func = accepted_functions[key]
                factor = None
                break
            else:
                if key in rht:
                    tmp2 = rht.split("_")
                    if not tmp2[1].isdigit():
                        print("Not a valid step function provided. Valid option are: 'pow_#', 'step_#', 'integer_divisor'.")
                        print(rht)
                        sys.exit()
                    if tmp2[0] == "step" or tmp2[0] == "pow":
                        rht_func = accepted_functions[key]
                        factor = tmp2[1]
                        break

        knob_values = rht_func(start, end, factor)
    else:
        knob_values = tmp1
    return knob_values, binding


def process_resource(descriptors):
    resources = []
    for desc in descriptors:
        if len(desc) !=3:
            print("Wrong format for 'resource' sweep option. Check the number of elements")
            print(desc)
            sys.exit()
        tag = desc[1]
        target_function = desc[0]
        values = desc[2]
        knob_values, knob_binding = parse_knob_literal_values(values)
        resource_obj = VivadoHLS.Resource(tag, target_function)
        binding = [(knob_binding, i) for i in range(len(knob_values))]
        resources.append((resource_obj, knob_values, binding))

    return resources


def process_inline(descriptors):
    inline = []
    for desc in descriptors:
        if len(desc) != 2:
            print("Wrong format for 'inline' sweep option. Check the number of elements.")
            print(desc)
            sys.exit()
        target_function = desc[0]
        values = desc[1]
        knob_values, knob_binding = parse_knob_literal_values(values)
        inline_obj = VivadoHLS.Inlining(target_function)
        binding = [(knob_binding, i) for i in range(len(knob_values))]
        inline.append((inline_obj, knob_values, binding))
    return inline


def process_unroll(descriptors):
    unroll = []
    for desc in descriptors:
        if len(desc) != 3:
            print("Wrong format for 'unroll' sweep option. Check the number of elements.")
            print(desc)
            sys.exit()
        target_function = desc[0]
        tag = desc[1]
        values = desc[2]
        knob_values, knob_binding = parse_knob_digit_values(values)
        unroll_obj = VivadoHLS.Unrolling(tag, target_function)
        binding_values = [(knob_binding, i) for i in range(len(knob_values))]
        unroll.append((unroll_obj, knob_values, binding_values))
    return unroll


def process_clock(descriptors):
    clock = []
    for desc in descriptors:
        if len(desc) != 1:
            print("Wrong format for 'clock' sweep option. Check the number of elements.")
            print(desc)
            sys.exit()

        values = desc[0]
        knob_values, knob_binding = parse_knob_digit_values(values)
        unroll_obj = VivadoHLS.Clock()
        binding_values = [(knob_binding, i) for i in range(len(knob_values))]
        clock.append((unroll_obj, knob_values, binding_values))

    return clock


def process_array_partition(descriptors):
    array_partition = []
    for desc in descriptors:
        #print(desc)
        if len(desc) != 5 and len(desc) != 4:
            print("Wrong format for 'array_partition' sweep option. Check the number of elements.")
            print(desc)
            sys.exit()

        target_function = desc[0]
        tag = desc[1]
        dimension = desc[2]
        partitioning_type = desc[3]
        if len(partitioning_type) == 10 and "complete" in partitioning_type:
            knob_values = ['complete']
            binding = [(None, '0')]
            array_partition_obj = VivadoHLS.Partition(tag, target_function, dimension)
            array_partition.append((array_partition_obj, knob_values, binding))
            continue
        else:
            values = desc[4]
            knob_partitioning_types, binding_partitioning_type = parse_knob_literal_values(partitioning_type)
            knob_partitioning_values, binding_partitioning_values = parse_knob_digit_values(values)
            array_partition_obj = VivadoHLS.Partition(tag, target_function, dimension)

        if "complete" in partitioning_type:
            partitioning_type.remove("complete")
            knob_values = [item for item in itertools.product(knob_partitioning_types, knob_partitioning_values)]
            binding = [(binding_partitioning_values, i % len(knob_partitioning_values)) for i in range(len(knob_values))]
            knob_values.append("complete")
        else:
            knob_values = [item for item in itertools.product(knob_partitioning_types, knob_partitioning_values)]
            binding = [(binding_partitioning_values, i) for i in range(len(knob_values))]
            array_partition.append((array_partition_obj, knob_values, binding))
    return array_partition


def process_pipeline(descriptors):
    for desc in descriptors:
        if len(desc) != 3:
            print("Wrong format for 'pipeline' sweep option. Check the number of elements.")
            print(desc)
            sys.exit()
    return


def create_ds(sweep_file):
    ds = {}
    with open(sweep_file) as f:
        content = f.readlines()

    f.close()
    content = [x.strip() for x in content]
    # Remove empty lines and comment lines
    for line in content:
        skip = False
        if line is "":
            continue
        for char in line:
            if char.isalpha():
                break
            if "#" == char:
                skip = True
                break
        if skip:
            continue

        tmp = line.split(";")
        knob_type = tmp[0]
        if knob_type not in VivadoHLS.hls_knobs:
            print("ERROR: " + knob_type + " is not a valid knob. Provide a valid sweep file")
            sys.exit()

        else:
            if knob_type in ds:
                content = ds.get(knob_type)
                content.append(tmp[1:])
                ds[knob_type] = content
            else:
                ds[knob_type] = [tmp[1:]]

    design_space_knob_values = []
    design_space_knob_type = []
    design_space_knob_obj = []
    design_space_knob_binding = []
    dictionary_keys = [key for key in ds.keys()]

    for k in range(len(dictionary_keys)):
        key = dictionary_keys[k]
        values = ds.get(key)

        if key == "resource":
            knobs = process_resource(values)
        if key == "unroll":
            knobs = process_unroll(values)
        if key == "clock":
            knobs = process_clock(values)
        if key == "pipeline":
            knobs = process_pipeline(values)
        if key == "inline":
            knobs = process_inline(values)
        if key == "array_partition":
            knobs = process_array_partition(values)

        for knob in knobs:
            design_space_knob_type.append(key)
            design_space_knob_obj.append(knob[0])
            design_space_knob_values.append(knob[1])
            design_space_knob_binding.append(knob[2])

    ds_obj = {
        "DS": ds,
        "Knobs_values": design_space_knob_values,
        "Knobs_type": design_space_knob_type,
        "Knobs": design_space_knob_obj,
        "Bindings": design_space_knob_binding
    }
    return ds_obj


