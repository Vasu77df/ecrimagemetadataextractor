"""
Now how do we get this info?
We could pull the docker image before OS build and extract that info.
But that means we have to run docker in codebuild and also pull the container image
which is slow, and also unecessary.

ECR follow the OCI container registry specification. This means we can curl against the container manifest,
and get the same info we need, all api calls no downloads much faster.

This program does this.
"""

import json
from logging import Logger, getLogger
from argparse import ArgumentParser
from os import environ

import boto3
import requests

logger: Logger = getLogger("ecrimagemetadataextractor")


class EcrImageMetadataExtractor:
    def __init__(self, image_uri: str, region: str) -> None:
        self.region = region
        # Create a Boto3 session we do this to specific the region we want to start the session against
        self.boto3_session = boto3.Session(region_name=region)
        # Create a client for the desired service
        self.ecr_client = self.boto3_session.client("ecr")
        self.account, self.registry, self.ecr_image_name, self.tag = self.parse_ecr_image(
            image_uri)
        # The default TTL for the ECR auth token is 12 hrs which is more the sufficient for this program
        self.auth_token = self.get_registry_auth_token()

    def parse_ecr_image(self, image_name: str) -> tuple[str, str, str, str]:
        """
        Parses an ECR image name from an Private ECR registry and returns the registry, repository, and tag.

        Args:
            image_name: name of image from private ECR container registry
            if not found use environment variable CODEBUILD_BUILD_IMAGE
        Returns:
            tuple: A tuple containing the account_id, registry, ecr_image_name, and tag.
        Example:
            Takes the env variable with an example value
            637423601711.dkr.ecr.us-east-1.amazonaws.com/container_image_repository:latest
            and Returns
            Account_id: 637423601711
            Registry: 637423601711.dkr.ecr.us-east-1.amazonaws.com
            Repository: container_image_repository
            Tag: latest
        """
        try:
            if image_name is None:
                image_name = environ["CODEBUILD_BUILD_IMAGE"]
        except KeyError:
            logger.error(
                "image_name argument is not supplied and could not find environment variable CODEBUILD_BUILD_IMAGE")
            logger.error(
                "We require and image name to parse metadata from.")
            exit(1)

        # Split the image name into its components
        parts = image_name.split("/")

        # Extract the AWS account ID
        aws_account_id = parts[0].split(".")[0]

        # Extract the registry URL
        registry_url = parts[0]

        # Extract the ECR image name and tag
        image_parts = parts[-1].split(":")

        image_name = image_parts[0]
        tag = image_parts[1]
        return aws_account_id, registry_url, image_name, tag

    def get_registry_auth_token(self) -> str:
        """
        Uses the clase object initalized ecr_client
        """
        auth_data = self.ecr_client.get_authorization_token(
            registryIds=[self.account])
        auth_token = auth_data["authorizationData"][0]["authorizationToken"]

        return auth_token

    def get_image_manifest(self) -> str | None:
        """
        Uses the class object initialized values of
        - registry
        - ecr_image_name
        - tag
        - auth_token
        """
        registry_url = f"https://{self.registry}"
        image_name = self.ecr_image_name
        image_digest_tag = self.tag
        request_token = self.auth_token

        request_url = f"{registry_url}/v2/{image_name}/manifests/{image_digest_tag}"
        logger.debug(f"This is the request url: {request_url}")
        request_headers = {
            "Authorization": f"Basic {request_token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        }
        response = requests.get(request_url, headers=request_headers)

        if response.status_code == 200:
            logger.info("Container Image manifest retrieved successfully!")
            manifest = json.loads(response.text)
            digest = manifest["config"]["digest"]
            return digest
        else:
            logger.error(
                f"Failed to retrieve Docker image manifest. Status code: {response.status_code}")
            logger.error(f"The error response: {response.text}")
            logger.error(
                "We need this to proceed or we can't track what's in your OS image exiting, check your ECR repo, the region for mismatches, Your codebuild role policy, ensure you have permissions to curl the repo"
            )
            exit(1)

    def get_digest_manifest(self, digest: str) -> dict:
        """
        Takes as argument the first digest sh256 of the container returned from the manifest

        Uses the class object initialized values of
        - registry
        - ecr_image_name
        - tag
        - auth_token
        """
        registry_url = f"https://{self.registry}"
        image_name = self.ecr_image_name
        request_token = self.auth_token
        request_url = f"{registry_url}/v2/{image_name}/blobs/{digest}"
        logger.debug(f"This is the request url: {request_url}")
        request_headers = {
            "Authorization": f"Basic {request_token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        }
        metadata_response = requests.get(request_url, headers=request_headers)

        if metadata_response.status_code == 200:
            logger.info("Container Image metadata retrieved successfully!")
            metadata_dict = dict(json.loads(metadata_response.text))
            logger.debug(f"This is the container metadata: \n {metadata_dict}")
            return metadata_dict
        else:
            logger.error(
                f"Failed to retrieve Docker image metadata. Status code: {metadata_response.status_code}")
            logger.error(f"The error response: {metadata_response.text}")
            logger.error(
                "We need this to proceed or we can't track what's in your OS image exiting, check your ECR repo, the region for mismatches, Your codebuild role policy, ensure you have permissions to curl the repo"
            )
            exit(1)


def capture_manifest(args: ArgumentParser) -> None:
    if args.region is not None:
        build_region = args.region
    elif (aws_region := environ.get("AWS_REGION")) is not None:
        build_region = aws_region
    else:
        logger.error(
            "Could not get build region, either use the --region argument or set the AWS_REGION env variable with region")
        exit(1)

    container_metadata_fetcher = EcrImageMetadataExtractor(
        args.image_id, build_region)
    if (manifest_digest := container_metadata_fetcher.get_image_manifest_digest()) is not None:
        logger.info(f"{manifest_digest}")
    else:
        logger.error(
            "We could get the manifest, something went wrong look at the stack trace above.")
        exit(1)
