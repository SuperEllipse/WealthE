# CML Community AMP Template Repo
This repo was designed as a template to be cloned for a barebones structure of a CML AMP application. This is meant to accelerate individuals wanting to contribute to the CML community AMPs repository.

**Applied ML Prototypes (AMPs)** provide reference example machine learning projects in Cloudera Machine Learning. These solutions to common problems in the machine learning field demonstrate how to fully use the power of Cloudera Machine Learning. AMPs allow you to create Cloudera Machine Learning projects to solve your own use cases.

AMPs are available to install and run from the Cloudera Machine Learning user interface. As new AMPs are developed, they will become available to you for your study and use. This repo attempts to make building your own easier.

## Building Your Own AMPs

One great use for AMPs is to showcase reference examples specific to your business by creating your own AMPs in-house. Once a data science project has been built in Cloudera Machine Learning, you can package it and have the Cloudera Machine Learning Admin add it to the AMP Catalog.

Each individual AMP requires a project metadata file, which defines the environmental resources needed by the AMP, and the setup steps to install the AMP in a Cloudera Machine Learning workspace. See Required Components below for details.

***Note****: You can store your AMPs in a git repo hosted on Github, Github Enterprise, or GitLab servers (not limited to github.com or gitlab.com.) Additionally, only simple authentication is supported, such as passing an API key, or including the username and password, as part of the URL. If additional authentication steps are required, then that git host is not supported.*

## Required Components

### AMP Build YAML
`.project-metadata.yaml` - (Required) Contains the Ansible-like runtime instructions which are a runbook for deploying the AMP, its pre-requisites and any requirements in CML to be an operational prototype.

Refer to https://docs.cloudera.com/machine-learning/cloud/applied-ml-prototypes/topics/ml-amp-project-spec.html for more information about the AMP Build script specifications.

### Catalog Entry YAML
`catalog-entry.yaml` - (Optional if managed by a central catalog) Contains the custom catalog entry used to route the AMPs catalog back to the source repo.

Refer to https://docs.cloudera.com/machine-learning/cloud/applied-ml-prototypes/topics/ml-amp-catalog-spec.html for more information about the AMP Catalog Entry specifications.

Additionally, https://docs.cloudera.com/machine-learning/cloud/applied-ml-prototypes/topics/ml-amp-custom-amp-catalog.html describes hosting custom AMP catalogs.

### Model Build Shell Script
`cdsw_build.sh` - (Optional in most cases) This file is required by Docker for building images. This is necessary if you are using AMPs to deploy a model in CML (CML-Native model).

Note that other than the `/samples` directory, the rest of the repo should stay "as is" and both the location of the files in the root directory (`/`) as well as the naming coventions are relevant.

## Required Folder Structure

There are several CML components to observe: **"Jobs", "Sessions", "Applications", "Models", and "Experiments"**. These should be observed as part of the AMP folder structuring in building community AMPs. For example, the following structure may parallel the contents of `/sample-project-metadata/project-metadata-sample-1.yaml`:

```yaml
/
  /0_session-verify-deps
  /1_session-install-deps
  /2_job-populate-vectordb
  /3_app
```

By following this general structure, `/<step number>_<CML Component>-<your task description>`, you can ensure consistency in how the repo is interpreted after it has been deployed and the users can easily understand the steps taken and if failure occured, which step it occured at.

## Adding custom catalog entries to your organization's instance of CML

The collection of AMPs available to end users can draw from one or more sources. For example, you might have an internal company catalog in addition to the default Cloudera catalog. The catalog must be provided with a catalog file and one or more project metadata YAML files.

Specify **Catalog File URL** if your git hosting service allows you to access the raw content of the repo without authenticating. (That is, the source files can be retrieved with a curl command, and do not require logging into a web page). Otherwise, specify the **Git Repository URL**. To use a git repository as a catalog source, the catalog file and the AMP files must be in a repository that can be cloned with **git clone** without authentication.

#### Steps to setup custom AMP

1. As an Administrator, go to **Site Administration > AMPs**.


2. Select **Git Repository URL** or **Catalog File URL** to specify a new source. Paste or enter the URL to the new source, and file name for the catalog file if necessary.


3. Click **Add Source**.
The catalog YAML file is loaded, and the projects found there are displayed in **Catalog Entries**.


4. If there are projects that are not yet ready for use, or that should not be displayed in the catalog, deselect **Enabled** in the **Catalog Entries**.
