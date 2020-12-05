# DB4HLS

Herein you can find the sources and the instruction to perform parallel DSEs using a [DSL](www.inf.usi.ch/phd/ferretti/db4hls/dsl.html) thought for an efficient definition of large design spaces, and to concurrently execute the synthesis with VivadoHLS using [gnu-parallel](https://www.gnu.org/software/parallel/).
Moreover, SQL scripts to interact with the [DB4HLS](www.inf.usi.ch/phd/ferretti/db4hls.html) database are provided in order to retrieve data from it.

### DB prerequisites:

1. mysql installed on your machine

### DB4HLS framework prerequisites:

1. python3
2. gnu-parallel

## How to use DB4HLS

After having installed mysql on your machine, import the [DB4HLS](www.inf.usi.ch/phd/ferretti/db4hls.html) schema available from the [follwing link](www.inf.usi.ch/phd/ferretti/db4hls.html) into your mysql database.

```
mysql -u <your_username> -p<your_password> db4hls < db4hls.sql
```
Now you can access DB4HLS and query it in order to access its data. Please refer to the [tutorial](inf.usi.ch/phd/ferretti/db4hls/tutorial.html) for more details regarding the SQL scripts and to the [DB4HLS documentation](inf.usi.ch/phd/ferretti/db4hls/docs.html) for more info about the database structure.

An sql script can be executed running the follwing instruction:
```sql
mysql -u <username> -p<username_password> -e "<sql_query>"
```
Example:
```sql
mysql -u lorenzo -pmypassword -e "SELECT * FROM db4hls.design;"
```
Will return the following output:
```
+--------------------+-----------+--------------+-----------------------------+------------------------+----------------+
| name               | id_design | id_algorithm | relative_path               | src_files              | testbench_file |
+--------------------+-----------+--------------+-----------------------------+------------------------+----------------+
| aes                |       428 |            1 | MachSuite/aes/aes           | aes.c, aes.h           |                |
| notable-noexpanded |         1 |            1 | MachSuite/aes/aes           | aes.c, aes.h           | aes_test.c     |
| table              |         3 |            1 | MachSuite/aes/aes           | aes.c, aes.h           | aes_test.c     |
| table-noexpanded   |         2 |            1 | MachSuite/aes/aes           | aes.c, aes.h           | aes_test.c     |
| ncubed             |         6 |            6 | MachSuite/gemm/ncubed       | gemm.c, gemm.h         |                |
| stencil2d          |       299 |          299 | MachSuite/stencil/stencil2d | stencil.c, stencil.h   |                |
| radix              |       335 |          335 | MachSuite/sort/radix        | sort.c, sort.h         |                |
| update             |       380 |          335 | MachSuite/sort/radix        | sort.c, sort.h         |                |
| backprop           |       365 |          338 | MachSuite/backprop/backprop | backprop.c, backprop.h |                |
| bulk               |       371 |          371 | MachSuite/bfs/bulk          | bfs.c, bfs.h           |                |
| fft                |       394 |          394 | MachSuite/fft/strided       | fft.c, fft.h           |                |
| strided            |       395 |          394 | MachSuite/fft/strided       | fft.c, fft.h           |                |
| knn                |       398 |          398 | MachSuite/md/knn            | md.c, md.h             |                |
| transpose          |       399 |          399 | MachSuite/fft/transpose     | fft.c, fft.h           |                |
| stencil3d          |       417 |          417 | MachSuite/stencil/stencil3d | stencil.c, stencil.h   |                |
| ellpack            |       419 |          419 | MachSuite/spmv/ellpack      | spmv.c, spmv.h         |                |
| blocked            |       420 |          420 | MachSuite/gemm/blocked      | gemm.c, gemm.h         |                |
| viterbi            |       425 |          425 | MachSuite/viterbi/viterbi   | viterbi.c, viterbi.h   |                |
| merge              |       450 |          450 | MachSuite/sort/merge        | sort.c, sort.h         |                |
+--------------------+-----------+--------------+-----------------------------+------------------------+----------------+
```

## How to use the DB4HLS framework

Run the `db4hls_config.sh` script. It will create a virtual environment and install all the python modules required.
Activate the virtual environment created with the following instruction:
```bash
source venv/bin/activate
```
Source the VivadoHLS script `settings64.sh` in order to run VivadoHLS from the DB4HLS folder.
Example of p
```bash
source <path_of_your_vivado_version>/settings64.sh
```
On my machine is:
```bash
source /local/tools/Xilinx/Vivado/2018.2/settings64.sh
```
NOTE: The venv activation and source of VivadoHLS script need to be re-run after each time you have closed your terminal.

Change the `main.py` python script according to your preferences and execute it in order to concurrently run an exhaustive exploration of the configuration space defined with the configuration space descriptor files.
Please see the content of `main.py` for an example of small exhaustive DSE exploration.

NOTE: The size of the design spaces grows exponentially with the number of knobs and the number of directive values considered. Therefore the exploration may generate a large number of designs and require a significant amount of time and resources.

### Folder structure

All the performed synthesis are generated in the `./syn/` folder. At the end of the exploration, the synthesis folders generated by VivadoHLS are compressed and saved in the `./syn_zip/` folder. Only the report file and the `.tcl` scrips are saved in order to reduce the amount of memory occupied by the exploration. The original folders are removed from `./syn/`, and only the log file of the synthesis process and the list of synthesized design is available in `./syn/`.
Similarly, the `./tcl_scripts/` is used to temporarily store the `.tcl` and `.dir` files automatically generated by the framework.
