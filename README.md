# Loom

A POSIX shell proteomics pipeline for designing consensus proteins, automatically weaving them from input FASTA files.

This pipeline follows the methodology outlined in [Sternke et. al., 2019](https://www.pnas.org/doi/full/10.1073/pnas.1816707116).

# Installation

## Dependencies

1. Python >= 3.12
2. Numpy >= 2.0.0
3. cd-hit
4. mafft
5. gzip (If using .gz compressed input files)
6. length_filter.py and build_consensus.py (Can be installed from this repository using `pip install .`

Install the required dependencies, then clone the repository and run `sudo make install` to install `loom` and its completions for all users.

Alternatively, put `loom` anywhere on your $PATH and make sure it's executable, and everything will function once the dependencies are installed.
You can manually install tab completions for Bash and Zsh by sourcing the included `loom-completion` file in your corresponding shell rc file.

The provided Dockerfile includes all necessary dependencies during its build process, and can be used as a standalone installation.

# Usage

Once you have installed Loom, it can be invoked as simply as `loom <INPUT_FASTA_FILE>`, and it will automatically generate a consensus protein from the provided FASTA.

By default it uses the following configuration:

- Sequences which deviate from the median by more than 30% will be removed. (Configurable via -l)
- Sequences above 90% identity will be removed during clustering. (Configurable via -i)
- Sequence positions above 50% gap frequency will be removed from the consensus protein. (Configurable via -g)

And the following performance configurations are also available:

- Clustering via cd-hit allows up to 4 GB of memory per input file. (Configurable via -m)
- Alignment via mafft uses one thread per input file. (Configurable via -t)
- While processing an input directory, one input file will be processed in parallel for each available CPU. (Configurable via -p)

The output file name (Configurable via -o), output directory (Configurable via -d), and working directory (Configurable via -w) are all also configurable. More information on the command line arguments can be found via `loom --help` or by reading the included Man page.

## Resuming a Run

If for any reason a run is interrupted, it can be resumed by providing the same input file or directory and the same working directory. Files will resume processing at the step where they left off.

## Performance Considerations

Clustering and aligning notably large input FASTA can be very memory and CPU intensive, and the pipeline as a whole generates many large intermediary files, meaning that a powerful workstation is often ideal when attempting to align many sequences simultaneously.

Loom has been tested and developed on Ubuntu 26.04 Linux with 96 GB of RAM and an Intel Core i9 Ultra 275HX CPU. It is primarily designed with workstations and HPC environments in mind, but for smaller input workloads, a conventional laptop which supports a POSIX shell should be sufficient.

In cases where memory is not a constraint, performance can often be improved by using a memory backed working directory, such as is provided by `mktemp -d` on a system where tempfs are backed by RAM.

# Uninstallation

If you installed with `sudo make install`, you can remove `loom` and its completions with `sudo make uninstall`.

Alternatively, just delete `loom` and its completion files if you installed it manually.

# Additional Tools

Included in this repository is a convenience helper for using loom with AlphaFold3. The `alphafold_input_parser.py` script parses a file in FASTA format into the JSON input format expected by AlphaFold3. It supports the following options for configuration:

- --version: The ALphaFold output format version you want to use.
- --dialect: 'alphafold3' or 'alphafoldserver' the AlphaFold dialect you want to use.
- --seed: A seed to enable reproducible results from AlphaFold.

# Bug Reports and Feature Requests

If you discover a bug or find an area where a feature is lacking, check the Github issues, and if one doesn't exist already, go ahead and open one.

# License

Loom is licensed under the terms of the [GNU GPL v3.0 License](LICENSE).
