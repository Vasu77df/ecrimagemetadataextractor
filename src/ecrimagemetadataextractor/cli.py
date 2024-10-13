import argparse
from logging import DEBUG
from enum import Enum
from typing import List, Literal

from ecrimagemetadataextractor.util import init_logger
from ecrimagemetadataextractor.capture_metadata import capture_manifest


class Verbs(Enum):
    get_manifest = "get_manifest"
    get_digest_metadata = "get_digest_metadata"

    def __str__(
        self,
    ) -> Literal["get_manifest", "get_digest_metadata"]:
        return self.value


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ecrimagemetadataextractor",
        description="Simple CLI tool to extract the image manifest from an AWS ECR hosted container",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "action",
        type=Verbs,
        choices=Verbs,
        help="Actions possible from the CLI, get_manifest: returns json manifest of container image, get_digest_metadata: returns json of first digest's manifest",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose logging", default=False
    )
    parser.add_argument(
        "-u", "--image-id", help="id of the container image in your registry example:", required=True
    )
    parser.add_argument(
        "-r", "--region", help="aws region to use", required=False
    )
    parsed_args = parser.parse_args(args)

    return parsed_args


def main(system_args: List[str]) -> None:
    parsed_args = parse_args(system_args)
    # init our log group for this program
    if parsed_args.verbose:
        init_logger(DEBUG)
    else:
        init_logger()

    if parsed_args.action == Verbs.get_manifest:
        capture_manifest(parsed_args)
    else:
        print("no action mentioned")
        exit(1)
