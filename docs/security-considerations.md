# Security Considerations

This configuration for Kubernetes is based on a configuration that was developed collaboratively for Security BSides in Portland Oregon aka _BSides PDX_.  

__The hardening measures taken were__:

* Run Calico overlay with implicit deny policies.
* Use RBAC
* Limit access to the AWS IAM Metdata Proxy
* Use lyft/metadataproxy to serve STS Tokens
* Ship logs from nodes and docker logs to cloudwatch using Fluent's daemonset.  
* Take a least privilege approach with AWS IAM for node / worker.
* Ensure Encryption of traffic to etc.  _cert based auth_
* Limit access to etcd from container data plane.  


__What if a long running instance (master, worker)__

In an ideal world we do not want instances in kubernetes to be long running.  However, sometimes this can happen.  _This is why I prefer to use Spot.  Spot can be your own chaos experiment if you set the price low enough ;) _.


## How do we do all the things?

You may be wondering how each of these features is implemented.  For some KOps does all the work for us.  For others it's as simple as Cloud-Init additions OR AWSRunCommand.  

If this does become a problem it's nice to be able to still audit attack surface and vulnerabilities across nodes.  For this reason we've added the AWS Inspector Agent via Cloud-Config to Masters and Nodes.  You can trigger using cloudwatch events a job to audit all boxes older than `n` hours, days, etc.

If inspector has findings you can use more security automation to help out.  Or simply terminate the node.  

## Use Calico

Calico usage is very simple in KOps.  Simply set:

```
networking:
  calico:
    crossSubnet: true
```

In the YAML file that's produced as an artifact of KOps.  The cross subnet setting is required when going multi-az.
It will also deploy a daemonset on a single kubernetes master to ensure that the src/dst ip check is disabled in the
networking settings.

## Use RBAC

Again KOps handles this for us.  

```
authorization:
  rbac: {}
```

> Turning RBAC on is easy.  Using it is the hard part.  TBD: A guide for creating a namespace and delegating a credential.  

## Limit Access to AWS metadataproxy

In order to do this we're manipulating `iptables` on the boxes themselves by extending the cloud-init.  

In the node spec note:

```yaml
additionalUserData:
- name: additionalHardening.sh
  type: text/x-shellscript
  content: |
    #!/bin/sh
    LOCAL_IPV4=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)

    /sbin/iptables \
      --append PREROUTING \
      --destination 169.254.169.254 \
      --protocol tcp \
      --dport 80 \
      --in-interface docker0 \
      --jump DNAT \
      --table nat \
      --to-destination $LOCAL_IPV4:8000 \
      --wait

    /sbin/iptables \
      --wait \
      --insert INPUT 1 \
      --protocol tcp \
      --dport 80 \
      \! \
      --in-interface docker0 \
      --jump DROP
```

> This will redirect all of the calls from the docker bridge to the metadataproxy container.  

## Deploy the Lyft metadataproxy

TBD

## Ship Logs to CloudWatch using a daemonset

TBD

## Least Privilege IAM using resource tags ( cluster can only cleanup after itself )

KOps policies are sufficiently hardened for this.  However, the two policies for the "node" and "master" have been extracted
and are updatable as part of the infosec-ansible-playbooks.  This is due to the fact that KOps does not let you make policies more
restrictive.  Only more permissive.  KOps also does not allow you to attach managed policies for service such as inspector or SSM.

## Ensure etcd has encrypted only traffic and cert based auth.

KOps does this for us and also generates an AWS KMS key for encryption of the etcd quorum's EBS volumes.

## Limit access to etcd.  Control the data-plane

TBD

## Our CI/CD Role for KOps to Deploy KubernetesClusters

TBD
