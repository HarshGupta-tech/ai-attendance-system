output "public_ip" {
  description = "The public IP address of the web server"
  value       = aws_instance.app_server.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the instance"
  value       = "ssh -i ${local_file.ssh_key.filename} ubuntu@${aws_instance.app_server.public_ip}"
}
