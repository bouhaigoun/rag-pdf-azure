variable "azure_storage_connection_string" {
  description = "Azure Storage connection string"
  sensitive   = true
}

variable "azure_search_endpoint" {
  description = "Azure AI Search endpoint"
}

variable "azure_search_key" {
  description = "Azure AI Search key"
  sensitive   = true
}

variable "mistral_api_key" {
  description = "Mistral API key"
  sensitive   = true
}

variable "n8n_api_key" {
  description = "n8n API key"
  sensitive   = true
}

variable "public_ip_sku" {
  description = "SKU for the public IP address"
  default     = "Standard"
}

variable "vm_size" {
  description = "Size of the Azure virtual machine"
  default     = "Standard_B2ms"
}