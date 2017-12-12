# Mozilla InfoSec Reference Implementation of Kubernetes

## Turning up a cluster for N00Bz

__Prod Exports__

```bash
export STAGE=prod
export AWS_REGION=us-west-2
export KOPS_STATE_STORE=s3://kops.security.mozilla.org
```

__Dev Exports__

```bash
export STAGE=dev
export AWS_REGION=us-west-2
export KOPS_STATE_STORE=s3://kops.security.allizom.org
```

## Learn All the things

__Docs__:

* [Why does this exist?](docs/why.md)
* [How to develop against the ansible play](docs/development.md)
* [Security Considerations](docs/security-considerations.md)
* [Cluster Defaults](docs/cluster-defaults.md)

## Creating a Cluster

```
ansible-playbook -c local ansible/find_or_create_single.yml -e clustername=${NAME}
```

## Deleting a Cluster

```
ansible-playbook -c local ansible/delete_single.yml -e clustername=${NAME}
```

## Exporting Admin Creds

```bash
kops export kubecfg
```
> Note that this decrypts and fetches the admin credential for the entire cluster.  Use RBAC for everything except setting up RBAC.

## Deploying the Kubernetes Dashboard

__Note:__ this may have been deployed for you depending on the state of our cluster defaults.

```bash
### From the cluster context.  ( You loaded the secrets )

kubectl create -f https://raw.githubusercontent.com/kubernetes/kops/master/addons/kubernetes-dashboard/v1.7.1.yaml

kops get secrets kube --type secret -oplaintext
```

> The username is admin and the password you've just retrieved from the secret store.  
The url is https://api.{$NAME}
