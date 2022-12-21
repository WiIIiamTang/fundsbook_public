# fundbook scripts public ver.

Automation tools

## Usage

From [releases](https://github.com/WiIIiamTang/fundsbook_public/releases). Only Windows is supported.

- Format of the workbook should be `.xlsm`
- The correct web driver needs to be in `app/drivers` (one is provided already but may not work if your browser has a different version)

## Developing locally

Create a new virtual environment and install the dependencies:

```
pip install -r requirements.txt
```

Run `run.sh` with the proper arguments to start what you want:

- `app`: Starts the app only
- `launcher`: Starts the launcher only
- `build`: Starts a clean build of the project
  - `build debug`: Starts a clean build of the project with debug mode
- `quickbuild`: Starts a build with cached files
- `clean`: Cleans the build and release files
- `test-dev`: Runs tests with `TEST_ENV` set to `dev`
- `test-prod`: Runs tests with `TEST_ENV` set to `prod`
- `tag`: Tags the current commit with the version number for release
  - `tag 1.0 1.0`: This example will tag the current commit with `v1.0+lu--1.0

### Releases

If a build passes all tests, `./run.sh tag` the commit for release. The first argument is the **app** version, while the second argument is the **launcher** version. **If a new tag is pushed to the repo, a new release will be created automatically,** so do not touch the releases page or the VERSION flags.

Releases are built and bundled according to the `.spec` files with pyinstaller (local releases will be in the `release` folder by default).
