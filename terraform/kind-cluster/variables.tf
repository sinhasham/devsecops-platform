variable "cluster_name" {
  description = "Name of the kind cluster"
  type        = string
  default     = "devsecops-platform-tf"
}

variable "node_image" {
  description = "Kubernetes node image to use"
  type        = string
  default     = "kindest/node:v1.34.0"
}
