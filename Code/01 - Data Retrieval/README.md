
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
  $ ~/anaconda/bin/pip install --upgrade geocoder
  ```

  * [github3.py docs](https://github3.readthedocs.io/en/develop/)
  * [PyMongo docs](http://api.mongodb.com/python/current/)
  * [Geocoder docs](https://geocoder.readthedocs.io)
  * [BeautifulSoup4 docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  * [Requests docs](http://docs.python-requests.org/en/master/)

4. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens), click on `Generate new token`, and enter your password.
   Pick something like `EPFL ADA Project` for the description, and click `Generate token`.

   Make also sure to create a [Geocoding API key](https://developers.google.com/maps/documentation/geocoding/get-api-key).

5. Create a file in this directory with the name `env.sh` and put the following inside, substituting `GH_TOKEN`, and `GAPI_KEY` with the tokens you just generated:

  ```bash
  # env.sh

  export GITHUB3_TOKEN="GH_TOKEN"
  export GOOGLE_API_KEY="GAPI_KEY"
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

Follow the same instructions as above, except for the following ones:

2. Download and Install MongoDB 3.4 from [its download page](https://www.mongodb.com/download-center).

6. Start MongoDB by running the following command from the `Code/` folder:

  ```
    "C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe" --dbpath=.\data\mongodb
  ```

7. Import the data by running the following command from the `Code/` folder:

  ```
  "C:\Program Files\MongoDB\Server\3.4\bin\mongorestore.exe" --drop --archive=dump\ada.archive --gzip --db ada
  ```

## Usage

Take a look at the [sample IPython notebook](../02 - Data Analysis/Example.ipynb) in the [`02 - Data Analysis`](../02 - Data Analysis/) folder.

## License

This code is released under the BSD3 license.

