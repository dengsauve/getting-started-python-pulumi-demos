"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources

# Setup
project = pulumi.get_project()
stack = pulumi.get_stack()
base_name = f"{project}-{stack}"
image_file = "assets/helloThere.jpeg"

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(f"{base_name}-rg")

# Create an Azure resource (Storage Account)
account = storage.StorageAccount(
    f"{base_name}-sa",
    account_name="demo1devsa",
    resource_group_name=resource_group.name,
    sku={
        "name": storage.SkuName.STANDARD_LRS,
    },
    kind=storage.Kind.STORAGE_V2,
    allow_blob_public_access=True,
    # enableHttpsTrafficOnly=False
)

# Create a Blob Container
container = storage.BlobContainer(
    f"{base_name}-images-ctr-1",
    account_name=account.name,
    public_access=storage.PublicAccess.BLOB,
    resource_group_name=resource_group.name,
)

# Export the primary key of the Storage Account
primary_key = (
    pulumi.Output.all(resource_group.name, account.name)
    .apply(
        lambda args: storage.list_storage_account_keys(
            resource_group_name=args[0], account_name=args[1]
        )
    )
    .apply(lambda accountKeys: accountKeys.keys[0].value)
)

# Upload the JPEG image as a Blob
blob = storage.Blob(
    f"{base_name}-image",
    resource_group_name=resource_group.name,
    account_name=account.name,
    container_name=container.name,
    type=storage.BlobType.BLOCK,
    source=pulumi.asset.FileAsset(image_file),
    content_type="image/jpeg",
)

# Build public URL
blob_url = pulumi.Output.concat(
    "https://", account.name, ".blob.core.windows.net/", container.name, "/", blob.name
)

pulumi.export("primary_storage_key", primary_key)
pulumi.export("hello_there_url", blob_url)