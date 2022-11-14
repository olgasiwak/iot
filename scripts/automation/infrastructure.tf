variable "IOT_API_KEY" {
    type = string
}

variable "root_password" {
  type = string
  sensitive = true
}

terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
    }
  }
}

provider "linode" {
    token = var.IOT_API_KEY
}

resource "linode_sshkey" "ssh_key" {
  label = "ssh_key"
  ssh_key = chomp(file("~/.ssh/iot.pub"))
}

resource "linode_instance" "iot-broker" {
    label = "broker"
    image = "linode/ubuntu20.04"
    region = "us-central"
    type = "g6-standard-1"
    authorized_keys = [linode_sshkey.ssh_key.ssh_key]
    root_pass = var.root_password

    group = "iot"
    tags = [ "iot", "poc" ]
    swap_size = 256
    private_ip = true
}

resource "linode_instance" "iot-client1" {
    label = "client1"
    image = "linode/ubuntu20.04"
    region = "us-central"
    type = "g6-standard-1"
    authorized_keys = [linode_sshkey.ssh_key.ssh_key]
    root_pass = var.root_password

    group = "iot"
    tags = [ "iot", "poc" ]
    swap_size = 256
    private_ip = true
}

resource "linode_instance" "iot-client2" {
    label = "client2"
    image = "linode/ubuntu20.04"
    region = "us-central"
    type = "g6-standard-1"
    authorized_keys = [linode_sshkey.ssh_key.ssh_key]
    root_pass = var.root_password

    group = "iot"
    tags = [ "iot", "poc" ]
    swap_size = 256
    private_ip = true
}
resource "linode_instance" "iot-vis" {
    label = "client2"
    image = "linode/ubuntu20.04"
    region = "us-central"
    type = "g6-standard-1"
    authorized_keys = [linode_sshkey.ssh_key.ssh_key]
    root_pass = var.root_password

    group = "iot"
    tags = [ "iot", "poc" ]
    swap_size = 256
    private_ip = true
}
