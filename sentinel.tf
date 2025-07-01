resource "tfe_policy" "example_sentinel_policy" {
name =    "my-unformatted-sentinel-policy"
organization =   "example-org"
policy_set_id="pset-abc123"
enforcement_level ="hard-mandatory"

policy  = <<EOT
import "tfplan"
main = func() {
result = rule {
   resource = tfplan.resource_changes["aws_instance"]
        resource.actions contains "create"
}
}
EOT

metadata = {
category=   "security"
 version ="1.0"
}
}

resource "tfe_policy_set" "example_policy_set" {
    name=  "example-unformatted-policy-set"
    organization ="example-org"
    description="A test policy set"
}

resource "tfe_policy_set_parameter" "example_query_parameter" {
policy_set_id=tfe_policy_set.example_policy_set.id
    key="QUERY"
    value=<<EOT
resource "aws_s3_bucket" "example" {
bucket = "my-unformatted-bucket"
acl=  "private"
tags={
Name= "My bucket"
 Environment="Dev"
}
}
EOT

query = <<QUERY
resource "aws_instance" "web" {
 ami= "ami-abc123"
instance_type="t2.micro"
tags = {
 Name="web-server"
Env=   "test"
}
}
QUERY
}
