"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage

from pulumi import ResourceOptions
from pulumi_gcp import compute

import pulumi_gcp
from pulumi import Output, Config
from pulumi_gcp.cloudrun import (
    ServiceTemplateMetadataArgs,
    ServiceTemplateSpecContainerEnvArgs,
)

## Storage
bucket = storage.Bucket('jwnlp-bucket')

## Compute Engine
compute_network = compute.Network(
    "network",
    auto_create_subnetworks=True,
)

compute_firewall = compute.Firewall(
    "firewall",
    network=compute_network.self_link,
    allows=[compute.FirewallAllowArgs(
        protocol="tcp",
        ports=["22", "80"],
    )]
)

# A simple bash script that will run when the webserver is initalized
startup_script = """#!/bin/bash
echo "Hello, World!" > index.html
nohup python -m SimpleHTTPServer 80 &"""

instance_addr = compute.address.Address("address")
compute_instance = compute.Instance(
    "instance",
    machine_type="f1-micro",
    metadata_startup_script=startup_script,
    boot_disk=compute.InstanceBootDiskArgs(
        initialize_params=compute.InstanceBootDiskInitializeParamsArgs(
            image="debian-cloud/debian-9-stretch-v20181210"
        )
    ),
    network_interfaces=[compute.InstanceNetworkInterfaceArgs(
            network=compute_network.id,
            access_configs=[compute.InstanceNetworkInterfaceAccessConfigArgs(
                nat_ip=instance_addr.address
            )],
    )],
    service_account=compute.InstanceServiceAccountArgs(
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    ),
    opts=ResourceOptions(depends_on=[compute_firewall]),
)

## PostgreSQL DB
config = Config()

cloud_sql_instance = pulumi_gcp.sql.DatabaseInstance(
    "jwnlp-db",
    database_version="POSTGRES_13",
    deletion_protection=False,
    settings=pulumi_gcp.sql.DatabaseInstanceSettingsArgs(tier="db-f1-micro"),
)

database = pulumi_gcp.sql.Database(
    "database", instance=cloud_sql_instance.name, name=config.require("db-name")
)

users = pulumi_gcp.sql.User(
    "users",
    name=config.require("db-name"),
    instance=cloud_sql_instance.name,
    password=config.require_secret("db-password"),
)

### Exporting Resources 

# Postgres DB
pulumi.export("cloud_sql_instance_name", cloud_sql_instance.name)

# Compute Engine
pulumi.export("instanceName", compute_instance.name)
pulumi.export("instanceIP", instance_addr.address)

# Storage
pulumi.export('bucket_name', bucket.url)
