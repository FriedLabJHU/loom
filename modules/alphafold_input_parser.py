#!/usr/bin/env python3
"""Rewrites a consensus protein into AlphaFold3 input format."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from warnings import warn

from .helpers import read_fasta


def main() -> None:  # noqa: PLR0915, C901
    """CLI for AlphaFold input parsing script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        metavar="Input FASTA file or directory",
        help="Input FASTA file or directory.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="Output JSON file",
        default=None,
        help="Output JSON Filename. Defaults to {INPUT_FILE}.json",
    )
    parser.add_argument(
        "-d",
        "--dialect",
        type=str,
        metavar="AlphaFold Dialect for output",
        default="alphafold3",
        choices=["alphafold3", "alphafoldserver"],
        help="Output AlphaFold3 dialect. Defaults to alphafold3 unless input FASTA contains multiple sequences.",
    )
    parser.add_argument(
        "-v",
        "--version",
        type=int,
        metavar="AlphaFold format Version for output",
        default=4,
        help="Output AlphaFold3 format version. Defaults to 4.",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        metavar="AlphaFold seed for model",
        default=42,
        help="Seed to use while running AlphaFold.",
    )
    args = parser.parse_args()

    if args.input.is_file():
        files_to_process = [args.input]
    elif args.input.is_directory():
        files_to_process = list(args.input.glob(".fa*"))
        files_to_process.extend(args.input.glob(".consensus"))
    else:
        msg = f"Input: {args.input} could not be processed as it is not a file or directory."
        raise RuntimeError(msg)

    output_json = args.output if args.output is not None else Path(f"{args.input.stem}.json")

    seqs = []
    ids = []
    for file in files_to_process:
        try:
            if file.suffix in [".gz", ".GZ", ".z", ".Z"]:
                with gzip.open(file, "rb") as fasta:
                    data = read_fasta(fasta, strip_gaps=False)
            else:
                with file.open("r") as fasta:
                    data = read_fasta(fasta, strip_gaps=False)

        except PermissionError as err:
            msg = f"Input file: {file} was not readable."
            raise PermissionError(msg) from err
        except FileNotFoundError as err:
            msg = f"Input file: {file} does not exist."
            raise FileNotFoundError(msg) from err

        seqs.extend(data[0])
        ids.extend(data[1])

    if len(seqs) == 0 or len(ids) == 0:
        msg = f"Input: {args.input} contained no valid sequences."
        raise RuntimeError(msg)

    ids = [identifier.lstrip(">") for identifier in ids]

    dialect = args.dialect

    if len(seqs) > 1 and dialect == "alphafold3":
        msg = f"Input: {args.input} contained multiple sequences, but dialect was set to 'alphafold'. Changing to 'alphafoldserver'."
        warn(msg, UserWarning, stacklevel=2)
        dialect = "alphafoldserver"

    match dialect:
        case "alphafold3":
            data = {
                "name": ids[0],
                "modelSeeds": [args.seed],
                "dialect": dialect,
                "version": args.version,
                "sequences": [{"protein": {"id": "A", "sequence": seqs[0]}}],
            }
        case "alphafoldserver":
            data = [
                {
                    "name": ids[i],
                    "modelSeeds": [args.seed],
                    "dialect": dialect,
                    "version": args.version,
                    "sequences": [{"protein": {"id": "A", "sequence": seqs[i]}}],
                }
                for i in range(len(ids))
            ]

    with output_json.open("a") as outfile:
        json.dump(data, outfile)


if __name__ == "__main__":
    main()
