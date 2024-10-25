# ecrimagemetadataextractor
Simple CLI tool to extract the image manifest and metadata from container images stored in a private AWS ECR registry

## Motivation
Take this scenario:
- You are running a build job, or a task in a container for example in AWS CodeBuild.
- While you are building the artifact you want to capture the details of the container you are using.
- You can capture the build environment metadata to your SBOM or just to capture metadata to check for reproducibility drifts or replicating the environment for troubleshooting.

This cli tool or library however you would like to use this, could be run within your container or out-of-band to capture a container's manifest and then it's metadata from the digest.


## Usage
```
usage: ecrimagemetadataextractor [-h] [-v] -u IMAGE_URI [-r REGION] {get_manifest,get_digest_metadata}

Simple CLI tool to extract the image manifest from private AWS ECR hosted container images

positional arguments:
  {get_manifest,get_digest_metadata}
                        Actions possible from the CLI, get_manifest: returns json manifest of container image,
                        get_digest_metadata: returns json of first digest's manifest

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose logging (default: False)
  -u IMAGE_URI, --image-uri IMAGE_URI
                        uri of the container image in your registry example: 772738948692.dkr.ecr.us-
                        east-1.amazonaws.com/os_build_env:latest (default: None)
  -r REGION, --region REGION
                        aws region to use (default: None)
```

### Get manifest
Command:
```
 python3 -m ecrimagemetadataextractor get_manifest --image-uri 772738948692.dkr.ecr.us-east-1.amazonaws.com/os_build_env:latest --region us-east-1 | jq . 
```
```
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
  "config": {
    "mediaType": "application/vnd.docker.container.image.v1+json",
    "size": 4552,
    "digest": "sha256:8a4a4313bd7cff420330aaf52e49da247b4c6107f44211d92db576e49b3f9659"
  },
  "layers": [
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 30610919,
      "digest": "sha256:802008e7f7617aa11266de164e757a6c8d7bb57ed4c972cf7e9f519dd0a21708"
    },
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 238910491,
      "digest": "sha256:6feaffcff6b9af7f741dfbc129b29e460ec4a1030c3c7684bc8ba15434982fcf"
    },
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 237477613,
      "digest": "sha256:6dbf3486e2803e0e2d67068727038e05da509de9335ca7cdc7664b7833da48ad"
    },
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 67232420,
      "digest": "sha256:e725b91ef7f278dd32339da93308782ab1af918204cf4d27082b374a089b159c"
    },
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 780,
      "digest": "sha256:b3f5b9a15490c9c075140c809857f4724263b6637a9466ee8708879cee5331e9"
    },
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 28832838,
      "digest": "sha256:f0eda69f6707fb23e5631437de1204664aad856f581270ba45ab5dadd0719e01"
    },
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 6235879,
      "digest": "sha256:c0cf9d8d47897c5a800086b3d4d80e28cc1653046b6795bccab4a9351025530a"
    }
  ]
}
```

### Get metadata from config digest
```
python3 -m ecrimagemetadataextractor get_digest_metadata --image-uri 772738948692.dkr.ecr.us-east-1.amazonaws.com/os_build_env:latest --region us-east-1 | jq .
{
  "architecture": "amd64",
  "config": {
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ],
    "Cmd": [
      "/bin/bash"
    ],
    "Labels": {
      "maintainer": "@vasuper",
      "org.opencontainers.image.ref.name": "ubuntu",
      "org.opencontainers.image.version": "24.04"
    }
  },
  "created": "2024-10-13T10:35:38.524849246-05:00",
  "history": [
    {
      "created": "2024-10-11T03:48:01.529767151Z",
      "created_by": "/bin/sh -c #(nop)  ARG RELEASE",
      "empty_layer": true
    },
    {
      "created": "2024-10-11T03:48:01.571862048Z",
      "created_by": "/bin/sh -c #(nop)  ARG LAUNCHPAD_BUILD_ARCH",
      "empty_layer": true
    },
    {
      "created": "2024-10-11T03:48:01.607507065Z",
      "created_by": "/bin/sh -c #(nop)  LABEL org.opencontainers.image.ref.name=ubuntu",
      "empty_layer": true
    },
    {
      "created": "2024-10-11T03:48:01.642491381Z",
      "created_by": "/bin/sh -c #(nop)  LABEL org.opencontainers.image.version=24.04",
      "empty_layer": true
    },
    {
      "created": "2024-10-11T03:48:03.777394067Z",
      "created_by": "/bin/sh -c #(nop) ADD file:34dc4f3ab7a694ecde47ff7a610be18591834c45f1d7251813267798412604e5 in / "
    },
    {
      "created": "2024-10-11T03:48:04.086892655Z",
      "created_by": "/bin/sh -c #(nop)  CMD [\"/bin/bash\"]",
      "empty_layer": true
    },
    {
      "created": "2024-10-13T10:33:50.683844544-05:00",
      "created_by": "LABEL maintainer=@vasuper",
      "comment": "buildkit.dockerfile.v0",
      "empty_layer": true
    },
    {
      "created": "2024-10-13T10:33:50.683844544-05:00",
      "created_by": "ARG DEBIAN_FRONTEND=noninteractive",
      "comment": "buildkit.dockerfile.v0",
      "empty_layer": true
    },
    {
      "created": "2024-10-13T10:33:50.683844544-05:00",
      "created_by": "RUN |1 DEBIAN_FRONTEND=noninteractive /bin/sh -c apt update -y && apt upgrade -y && apt install -y     aptly     bubblewrap     ca-certificates     cpio     curl     debian-archive-keyring     dosfstools     e2fsprogs      git     kmod     procps     python3-cryptography     python3-pip     python3-setuptools     python3-venv     python3-wheel     rauc     sbsigntool     squashfs-tools     systemd     systemd-boot     systemd-repart     systemd-ukify     systemd-container     mtools     tpm2-tools     ubuntu-keyring     unzip     zstd # buildkit",
      "comment": "buildkit.dockerfile.v0"
    },
    {
      "created": "2024-10-13T10:34:17.339702189-05:00",
      "created_by": "RUN |1 DEBIAN_FRONTEND=noninteractive /bin/sh -c apt install -y libc6 groff less     && curl \"https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip\" -o \"awscliv2.zip\"     && ls -alh     && unzip ./awscliv2.zip     && ./aws/install # buildkit",
      "comment": "buildkit.dockerfile.v0"
    },
    {
      "created": "2024-10-13T10:34:25.791326946-05:00",
      "created_by": "RUN |1 DEBIAN_FRONTEND=noninteractive /bin/sh -c curl -o /tmp/amazon-ssm-agent.deb https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_amd64/amazon-ssm-agent.deb     && dpkg -i /tmp/amazon-ssm-agent.deb     && curl -o /etc/amazon/ssm/amazon-ssm-agent.json https://raw.githubusercontent.com/aws/aws-codebuild-docker-images/master/ubuntu/standard/5.0/amazon-ssm-agent.json # buildkit",
      "comment": "buildkit.dockerfile.v0"
    },
    {
      "created": "2024-10-13T10:34:26.437300051-05:00",
      "created_by": "RUN |1 DEBIAN_FRONTEND=noninteractive /bin/sh -c rm --force --recursive /var/lib/apt/lists/*     && rm --force --recursive /usr/share/doc     && rm --force --recursive /usr/share/man     && apt clean # buildkit",
      "comment": "buildkit.dockerfile.v0"
    },
    {
      "created": "2024-10-13T10:34:32.860798461-05:00",
      "created_by": "RUN |1 DEBIAN_FRONTEND=noninteractive /bin/sh -c rm --force /usr/lib/python3.12/EXTERNALLY-MANAGED &&     apt-get update &&     apt-get install -y python3-pip &&     pip install pefile # buildkit",
      "comment": "buildkit.dockerfile.v0"
    },
    {
      "created": "2024-10-13T10:35:38.524849246-05:00",
      "created_by": "RUN |1 DEBIAN_FRONTEND=noninteractive /bin/sh -c python3 -m venv mkosivenv     && mkosivenv/bin/pip install git+https://github.com/systemd/mkosi.git@v24.3     && mkosivenv/bin/mkosi --version # buildkit",
      "comment": "buildkit.dockerfile.v0"
    }
  ],
  "os": "linux",
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:a46a5fb872b554648d9d0262f302b2c1ded46eeb1ef4dc727ecc5274605937af",
      "sha256:99423e0f187f5cdb62e47051984634a6d11e157d3127ae506562857f80493928",
      "sha256:aea99ec45e93114c710f03e635dfafd7320f429740cd5087822bc98365882429",
      "sha256:fc1645534d5bec025b2a6fc13483396cd20184edcfe06580cc86579d0b2067cd",
      "sha256:048f3fe585e6ebf6a57286b71bed90acc19fe8fef1410e898ccde7a42735fba8",
      "sha256:47ea983fc16a48b103cf6faf2bc97ecca8463052e570651c5690c1dbfab0539c",
      "sha256:76a0f1399709e7d3f747cd0380359338142de988544f5dea6298976afca4333b"
    ]
  }
}
```

## How does this work?

To pull metdata from a container layer, We could pull the docker image within the running environment and extract the info. But that means we have to run docker in our environment and also pull the container image which is slow, and also unecessary.

ECR follow the OCI container registry specification. This means we can curl against the container manifest,
and get the same info we need, all api calls, no downloads much faster.

- https://specs.opencontainers.org/distribution-spec/?v=v1.0.0

## Managing the project

I use [uv](https://docs.astral.sh/uv/) to manage this project. 

Here are some common things to run to manage the project 

- Setup an venv of the project
```
uv venv 
```

- Run the type checker mypy

```
uv run mypy src
```
TODO: Fix the boto3 import error

- Run unit tests

```
uv run python -m pytest tests/
```
