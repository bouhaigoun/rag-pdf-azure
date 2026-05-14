terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rag_prod" {
  name     = "rg-rag-pdf-prod"
  location = "France Central"
}

resource "azurerm_virtual_network" "rag_vnet" {
  name                = "vnet-rag-prod"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rag_prod.location
  resource_group_name = azurerm_resource_group.rag_prod.name
}

resource "azurerm_subnet" "rag_subnet" {
  name                 = "subnet-rag-prod"
  resource_group_name  = azurerm_resource_group.rag_prod.name
  virtual_network_name = azurerm_virtual_network.rag_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "rag_ip" {
  name                = "pip-rag-prod"
  location            = azurerm_resource_group.rag_prod.location
  resource_group_name = azurerm_resource_group.rag_prod.name
  allocation_method   = "Static"
  sku                 = var.public_ip_sku
}

resource "azurerm_network_security_group" "rag_nsg" {
  name                = "nsg-rag-prod"
  location            = azurerm_resource_group.rag_prod.location
  resource_group_name = azurerm_resource_group.rag_prod.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "n8n"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5678"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Flask"
    priority                   = 1003
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "rag_nic" {
  name                = "nic-rag-prod"
  location            = azurerm_resource_group.rag_prod.location
  resource_group_name = azurerm_resource_group.rag_prod.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.rag_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.rag_ip.id
  }
}

resource "azurerm_network_interface_security_group_association" "rag_nic_nsg" {
  network_interface_id      = azurerm_network_interface.rag_nic.id
  network_security_group_id = azurerm_network_security_group.rag_nsg.id
}

resource "azurerm_linux_virtual_machine" "rag_vm" {
  name                = "vm-rag-prod"
  resource_group_name = azurerm_resource_group.rag_prod.name
  location            = azurerm_resource_group.rag_prod.location
  size                = var.vm_size
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.rag_nic.id
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  custom_data = base64encode(<<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker azureuser
    cd /home/azureuser
    git clone https://github.com/bouhaigoun/rag-pdf-azure.git
    cd rag-pdf-azure
    cp .env.example .env
  EOF
  )
}

output "vm_public_ip" {
  value = azurerm_public_ip.rag_ip.ip_address
}