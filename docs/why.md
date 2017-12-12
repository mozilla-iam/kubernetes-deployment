# Why does this exist?

You may be asking: _Why would anyone wrap a tool like KOps with ansible?_  The answer is simply
that there are a few things that you __can not__ yet do with KOps that ansible is good at facilitating.  

Through the versions of KOps there has been one user story that has stayed in the foreground and
that story is _As an admin I can create one KOps configuration that is replicatable regardless
of region, availability zone, or account._ Additionally it is also nice to be able to continuous
integrate and continuously deliver that configuration idempotently without loss of service to the
cluster itself.  

At Mozilla in the Identity and Access Management project we primarily work in two accounts.  

* InfoSec Dev
* InfoSec Prod

Both of these account have some route53 zone that is associated with them.

* security.allizom.org (Dev)
* security.mozilla.org (Prod)

## Templating with KOps using GoLang

In this dual account case the test case simple.  

1. Create 1 KOps Config
2. Write some glue code.  _very very little glue code_
3. Be able to deploy into each account using `codepipeline, codebuild` in two AWS regions.

## KOps 1.8 a Game Changer

Kops 1.8 introduced the ability to use standard GoLang templates and dry-run a configuration.
From there you could set vars and create a parameters file to render a final template.  

Template variables themselves are arbitrary.  You can make the names however you like to match
your standard convention. (_if you have one_)

```golang
  name: {{.name}}
```

> Above you'll see an example of the use of a variable called .name.  

In order to populate that variable at run time all that needs to be done is _create
a variable file_.  The mission of a values file is simple.  

1. Provide data.
2. Render Templates
3. Keep Flying

Variable don't get a `---` header like in some templating languages.  They are simply key: value.

```yaml
name: us-west-2.infra.security.allizom.org
maxPrice: "0.04"
awsRegion: us-west-2
zoneId: Z1AY0K1T7473M8
kopsState: s3://kops.security.allizom.org/
```

> Above is an example of the variables file used to drive cluster creation across these two accounts.  

## Using the Template

Using the template and variables to provision a cluster is simple.  It is a 2-step process.

1. Render the template
2. Apply the template

### Sample usage
```bash
export STAGE=dev
export AWS_REGION=us-west-2
kops toolbox template --values values/${STAGE}/${AWS_REGION}.yml --template cluster-1.0.yml > rendered-templates/${STAGE}-${AWS_REGION}.yml
rendered-templates/${STAGE}-${AWS_REGION}.yml
kops create -f rendered-templates/${STAGE}-${AWS_REGION}.yml
kops create secret --name ${NAME} sshpublickey admin -i ~/.ssh/infosec-infra.pub
kops update cluster ${NAME} --yes
```

> Note: That in the above VARS file we used a variable to abstract out things like kubernetes state store and route53 zone.  
