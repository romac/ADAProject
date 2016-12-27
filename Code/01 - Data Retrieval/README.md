
# Data Retrieval

## Setup

1. Install the required Python libraries

```bash
$ ~/anaconda/bin/pip install --pre github3.py
$ ~/anaconda/bin/pip install dataset
```

2. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens), click on `Generate new token`, and enter your password.
Pick something like `EPFL ADA Project` for the description, and click `Generate token`.

3. Create a file in this directory with the name `env.sh` and put the following inside, substituting `GH_TOKEN` with the token you just generated:

```bash
# env.sh

export GITHUB3_TOKEN="GH_TOKEN"
```

This file is ignored by Git, so don't worry about accidentally committing your token.

## Usage

```bash
~/anaconda/bin/python3 dataRetrieval.py
```

## License

This code is released under the BSD3 license.

