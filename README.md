# in-toto demo [![CI](https://github.com/in-toto/demo/actions/workflows/ci.yml/badge.svg)](https://github.com/in-toto/demo/actions/workflows/ci.yml)

## 본 저장소는 in-toto의 공식 데모 코드를 기반으로 교육 목적에 맞게 최적화된 버전입니다.<br>원본 코드의 저작권은 in-toto에 귀속되어 있으며,<br>수정 및 한글화된 버전의 저작권은 본인에게 있습니다.<br><br>한글 문서가 필요하신 경우 개별 문의 부탁드립니다.
## This repository is an educational adaptation of the official in-toto demo code, optimized for training purposes. The original codebase is copyrighted by in-toto, while the modifications and Korean localization are copyrighted by the repository owner. <br><br>Please contact me if you need documentation in Korean.
In this demo, we will use in-toto to secure a software supply chain with a very
simple workflow. kang is a developer for a project, kim packages the software, and
lee oversees the project.  So, using in-toto's names for the parties, 
lee is the project owner - she creates and signs the software supply chain
layout with her private key - and kang and kim are project functionaries -
they carry out the steps of the software supply chain as defined in the layout.

For the sake of demonstrating in-toto, we will have you run all parts of the
software supply chain.
This is, you will perform the commands on behalf of lee, kang and kim as well
as the client who verifies the final product.


## Download and setup in-toto on \*NIX (Linux, OS X, ..)
__Virtual Environments (optional)__

We highly recommend installing `in-toto` and its dependencies in a
[`venv`](https://docs.python.org/3/library/venv.html) Python virtual
environment. Just copy-paste the following snippet to create a virtual
environment:

```bash
# Create the virtual environment
python3 –m venv .demo

# Activate the virtual environment
# This will add the prefix "(in-toto-demo)" to your shell prompt
source .demo/bin/activate
```

__Get demo files and install in-toto__
```bash
# Fetch the demo repo using git
git clone https://github.com/junskr/in-toto-demo.git

# Change into the demo directory
cd in-toto-demo

# Install a compatible version of in-toto
pip3 install -r requirements.txt
```
*Note: If you are having troubles installing in-toto, make sure you have all
the system dependencies. See the [installation guide on
in-toto.readthedocs.io](https://in-toto.readthedocs.io/en/latest/installing.html)
for details.*

Inside the demo directory you will find four directories: `owner_lee`,
`developer_kang`, `developer_kim` and `final_product`. lee, kang and kim
already have RSA keys in each of their directories. This is what you see:
```bash
tree  # If you don't have tree, try 'find .' instead
# the tree command gives you the following output
# .
# ├── README.md
# ├── demo-clean.py
# ├── final_product
# │   ├── .keep
# ├── developer_kang
# │   ├── kang
# │   └── kang.pub
# ├── developer_kim
# │   ├── kim
# │   └── kim.pub
# ├── owner_lee
# │   ├── lee
# │   ├── lee.pub
# │   └── create_layout.py
# └── requirements.txt
```

## Run the demo commands
Note: if you don't want to type or copy & paste commands and would rather watch
a script run through the commands, jump to [the last section of this document](#tired-of-copy-pasting-commands)

### Define software supply chain layout (lee)
First, we will need to define the software supply chain layout. To simplify this
process, we provide a script that generates a simple layout for the purpose of
the demo.

In this software supply chain layout, we have lee, who is the project
owner that creates the layout, kang, who clones the project's repo and
performs some pre-packaging editing (update version number), and kim, who uses
`tar` to package the project sources into a tarball, which
together with the in-toto metadata composes the final product that will
eventually be installed and verified by the end user.

```shell
# Create and sign the software supply chain layout on behalf of lee
cd owner_lee
python create_layout.py
```
The script will create a layout, add kang's and kim's public keys (fetched from
their directories), sign it with lee's private key and dump it to `root.layout`.
In `root.layout`, you will find that (besides the signature and other information)
there are three steps, `clone`, `update-version` and `package`, that
the functionaries kang and kim, identified by their public keys, are authorized
to perform.

### Clone project source code (kang)
Now, we will take the role of the developer kang and perform the step
`clone` on his behalf, that is we use in-toto to clone the project repo from GitHub and
record metadata for what we do. Execute the following commands to change to kang's
directory and perform the step.

```shell
cd ../developer_kang
in-toto-run --step-name clone --use-dsse --products in-toto-demo-project/foo.py --signing-key kang -- git clone https://github.com/junskr/in-toto-demo-project.git
```

Here is what happens behind the scenes:
 1. In-toto wraps the command `git clone https://github.com/junskr/in-toto-demo-project.git`,
 1. hashes the contents of the source code, i.e. `in-toto-demo-project/foo.py`,
 1. adds the hash together with other information to a metadata file,
 1. signs the metadata with kang's private key, and
 1. stores everything to `clone.[kang's keyid].link`.

### Update version number (kang)
Before kim packages the source code, kang will update
a version number hard-coded into `foo.py`. He does this using the `in-toto-record` command,
which produces the same link metadata file as above but does not require kang to wrap his action in a single command.
So first kang records the state of the files he will modify:

```shell
# In developer_kang directory
in-toto-record start --step-name update-version --use-dsse --signing-key kang --materials in-toto-demo-project/foo.py
```

Then kang uses an editor of his choice to update the version number in `demo-project/foo.py`, e.g.:

```shell
sed -i.bak 's/v0/v1/' in-toto-demo-project/foo.py && rm in-toto-demo-project/foo.py.bak
```

And finally he records the state of files after the modification and produces
a link metadata file called `update-version.[kang's keyid].link`.
```shell
# In developer_kang directory
in-toto-record stop --step-name update-version --use-dsse --signing-key kang --products in-toto-demo-project/foo.py
```

kang has done his work and can send over the sources to kim, who will create
the package for the user.

```shell
# kang has to send the update sources to kim so that he can package them
cp -r in-toto-demo-project/ ../developer_kim/
```

### Package (kim)
Now, we will perform kim’s `package` step by executing the following commands
to change to kim's directory and create a package of the software project

```shell
cd ../developer_kim
in-toto-run --step-name package --use-dsse --materials in-toto-demo-project/* --products in-toto-demo-project.tar.gz --signing-key kim --exclude ".git" -- tar  -zcvf in-toto-demo-project.tar.gz in-toto-demo-project
```

This will create another step link metadata file, called `package.[kim's keyid].link`.
It's time to release our software now.

### Generate SBOM (kim)
```shell
syft in-toto-demo-project/* -o cyclonedx-json > sbom.json
in-toto-run --step-name generate-sbom --use-dsse --products sbom.json --signing-key kim --no-command
```

### Verify final product (client)
Let's first copy all relevant files into the `final_product` that is
our software package `demo-project.tar.gz` and the related metadata files `root.layout`,
`clone.[kang's keyid].link`, `update-version.[kang's keyid].link` and `package.[kim's keyid].link`:
```shell
cd ..
cp owner_lee/root.layout developer_kang/clone.210dcc50.link developer_kang/update-version.210dcc50.link developer_kim/package.be06db20.link developer_kim/in-toto-demo-project.tar.gz developer_kim/generate-sbom.be06db20.link developer_kim/sbom.json final_product
```
And now run verification on behalf of the client:
```shell
cd final_product
# Fetch lee's public key from a trusted source to verify the layout signature
# Note: The developer public keys are fetched from the layout
cp ../owner_lee/lee.pub .
in-toto-verify --layout root.layout --verification-keys lee.pub
```
This command will verify that
 1. the layout has not expired,
 2. was signed with lee’s private key,
<br>and that according to the definitions in the layout
 3. each step was performed and signed by the authorized developer
 4. the recorded materials and products follow the artifact rules and
 5. the inspection `untar` finds what it expects.


From it, you will see the meaningful output `PASSING` and a return value
of `0`, that indicates verification worked out well:
```shell
echo $?
# should output 0
```

### Tampering with the software supply chain
Now, let’s try to tamper with the software supply chain.
Imagine that someone got a hold of the source code before kim could package it.
We will simulate this by changing `in-toto-demo-project/foo.py` on kim's machine
(in `developery_kim` directory) and then let kim package and ship the
malicious code.

```shell
cd ../developer_kim
echo print("hi") >> in-toto-demo-project/foo.py
```
kim thought that this is the genuine code he got from kang and
unwittingly packages the tampered version of foo.py

```shell
in-toto-run --step-name package --use-dsse --materials in-toto-demo-project/* --products in-toto-demo-project.tar.gz --signing-key kim --exclude ".git" -- tar  -zcvf in-toto-demo-project.tar.gz in-toto-demo-project
```
and ships everything out as final product to the client:
```shell
cd ..
cp owner_lee/root.layout developer_kang/clone.210dcc50.link developer_kang/update-version.210dcc50.link developer_kim/package.be06db20.link developer_kim/in-toto-demo-project.tar.gz developer_kim/generate-sbom.be06db20.link developer_kim/sbom.json final_product
```

### Verifying the malicious product

```shell
cd final_product
in-toto-verify --layout root.layout --verification-keys lee.pub
```
This time, in-toto will detect that the product `foo.py` from kang's `update-version`
step was not used as material in kim's `package` step (the verified hashes
won't match) and therefore will fail verification an return a non-zero value:
```shell
echo $?
# should output 1
```


### Wrapping up
Congratulations! You have completed the in-toto demo! This exercise shows a very
simple case in how in-toto can protect the different steps within the software
supply chain. More complex software supply chains that contain more steps can be
created in a similar way. You can read more about what in-toto protects against
and how to use it on [in-toto's Github page](https://in-toto.github.io/).

## Cleaning up and automated run through
### Clean slate
If you want to run the demo again, you can use the following script to remove all the files you created above.

```bash
cd .. # You have to be the demo directory
python demo-clean.py
```
