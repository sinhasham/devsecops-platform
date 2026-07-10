output "cluster_name" {
  description = "Name of the created kind cluster"
  value       = kind_cluster.devsecops.name
}

output "kubeconfig" {
  description = "Kubeconfig for the created cluster"
  value       = kind_cluster.devsecops.kubeconfig
  sensitive   = true
}
