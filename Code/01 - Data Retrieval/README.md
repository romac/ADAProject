
# Data Retrieval

## Setup

### OS X

1. [Install Homebrew](http://brew.sh/):

  ```bash
  $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  ```

2. [Install MongoDB](https://docs.mongodb.com/master/tutorial/install-mongodb-on-os-x/):  
  **IMPORTANT: Make sure to install MongoDB 3.4**

  ```bash
  $ brew update
  $ brew install mongodb
  ```

3. Install the required Python libraries:

  ```bash
  $ ~/anaconda/bin/pip install --pre github3.py
  $ ~/anaconda/bin/pip install --upgrade pymongo
  $ ~/anaconda/bin/pip install --upgrade BeautifulSoup4
  $ ~/anaconda/bin/pip install --upgrade requests
  ```

  * [github3.py docs](https://github3.readthedocs.io/en/develop/)
  * [PyMongo docs](http://api.mongodb.com/python/current/)

4. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens), click on `Generate new token`, and enter your password.
   Pick something like `EPFL ADA Project` for the description, and click `Generate token`.

5. Create a file in this directory with the name `env.sh` and put the following inside, substituting `GH_TOKEN` with the token you just generated:

  ```bash
  # env.sh

  export GITHUB3_TOKEN="GH_TOKEN"
  export MONGO_HOST="localhost"
  export MONGO_PORT=27017
  ```

  This file is ignored by Git, so don't worry about accidentally committing your token.

6. Start MongoDB by running the following command from the `Code/` folder, in a new tab:

  ```bash
  $ mongod -f mongod.conf
  ```

7. We now need to import the data in our local MongoDB database.
   To do so, just run the following command from the `Code` directory:

  ```bash
  $ make mongo_restore
  ```

### Linux

Follow the same steps as for OS X, except for the first two ones. Instead, install
MongoDB using your favorite package manager.

### Windows

???

## License

This code is released under the BSD3 license.

