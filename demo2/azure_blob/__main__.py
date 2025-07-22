import pulumi
import pulumi_azure_native as azure_native

# Create an Azure Resource Group
resource_group = azure_native.resources.ResourceGroup("resourceGroup")

# Create an Azure Storage Account
storage_account = azure_native.storage.StorageAccount("storageAccount",
    resource_group_name=resource_group.name,
    sku=azure_native.storage.SkuArgs(
        name=azure_native.storage.SkuName.STANDARD_LRS,
    ),
    kind=azure_native.storage.Kind.STORAGE_V2
)

# Create a public Blob Container
blob_container = azure_native.storage.BlobContainer("blobContainer",
    resource_group_name=resource_group.name,
    account_name=storage_account.name,
    public_access=azure_native.storage.PublicAccess.BLOB
)

# Export the storage account name, container name, and public Blob URL prefix
pulumi.export("storage_account_name", storage_account.name)
pulumi.export("container_name", blob_container.name)
pulumi.export("public_blob_url_prefix", pulumi.Output.concat("https://", 
    storage_account.name, ".blob.core.windows.net/", blob_container.name, "/"))