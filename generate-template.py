"""Generating CloudFormation template."""

from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
)


ApplicationPort = "5000"


t = Template() 

t.add_description("HelloWorld web application") 

# Add a Security Group to the template with inbound rules for SSH on Port 22
# and for TCP on port 5000
t.add_resource(ec2.SecurityGroup(
    "SecurityGroup",
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp="0.0.0.0/0",
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0",
        ),
    ],
))

# Create a parameter for your template to accept which key pair to use when launching the template 
t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="name of an existing EC2 KeyPair.",
))

# Create the set of commands to execute when ec2 instance is created
ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo yum update",
    "sudo yum install python3 -y",
    "sudo pip3 install flask",
    "echo 'y' | sudo yum install curl-devel expat-devel gettext-devel openssl-devel zlib-devel",
    "echo 'y' | sudo yum install git-core",
    "sudo git clone https://github.com/Mukunda9000/ci-cd-demo.git",
    "cd ci-cd-demo",
    "sudo python3 ./src/app.py"
]))

# Create ec2 instance with the Sec Group,  Key Pair
t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-082b5a644766e0e6f",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
)) 

# Add PublicIp of the instance to the output of CloudFormation execution
t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp"),
))

# Add Application Endpoint to the output of CloudFormation execution
t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ]),
)) 

print(t.to_json())
