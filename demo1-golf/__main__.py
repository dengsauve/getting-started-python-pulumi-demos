import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources

resource_group = resources.ResourceGroup("demo1-rg")

account = storage.StorageAccount(
    "demo1devsa",
    resource_group_name=resource_group.name,
    sku={
        "name": storage.SkuName.STANDARD_LRS,
    },
    kind=storage.Kind.STORAGE_V2,
    allow_blob_public_access=True,
)

container = storage.BlobContainer(
    "demo1-images-ctr-1",
    account_name=account.name,
    public_access=storage.PublicAccess.BLOB,
    resource_group_name=resource_group.name,
)

primary_key = (
    pulumi.Output.all(resource_group.name, account.name)
    .apply(
        lambda args: storage.list_storage_account_keys(
            resource_group_name=args[0], account_name=args[1]
        )
    )
    .apply(lambda accountKeys: accountKeys.keys[0].value)
)

blob = storage.Blob(
    "demo1-image",
    resource_group_name=resource_group.name,
    account_name=account.name,
    container_name=container.name,
    type=storage.BlobType.BLOCK,
    source=pulumi.asset.FileAsset("assets/helloThere.jpeg"),
    content_type="image/jpeg",
)