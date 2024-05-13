# T\<env\>plate

A way to generate `.env` files from a template file using remote sources.

Currently supports the following remote sources:

- azure keyvault secrets (assumes the *az cli* is is installed and configured)
- kubernetes secrets & configmaps (assumes the *kubectl cli* is installed and configured)

## Usage

1. Install the package. I recommend the use of `pipx` to install it in a global and isolated enviroment: 
   `pipx install tenvplate`

2. Create a .env.template with the following format:
   ```env
   # comment, will be ignored
   FIXED=will-be-left-untouched
   ENV_VAR_FROM_K8S_SECRET={{kubernetes/<name-space-name>/secrets/<secret-name>/<secret-field>}}
   ENV_VAR_FROM_K8S_CONFIGMAP={{kubernetes/<name-space-name>/configmaps/<configmap-name>/<configmap-field>}}
   ENV_VAR_FROM_AZURE_KEYVAULT={{azure-keyvault/<keyvault-name>/secrets/<secret-name>}}
   ```

3. Run the following command to generate an environment file simply run `tenvplate`. Optional arguments are:
   - `--src-path` to specify the template file (default `.env.template` in the working directory)
   - `--dst-path` to specify the destination file (default `.env` in the same directory as the template file)


## Contributing
To setup the development environment and run linting and testing:
```
python -m venv .venv
source .venv/Scripts/activate  # or .venv/bin/activate on linux
pip install -e .[dev]
poe all
```

To test the install with pipx `pipx install . --force`

To build the package: `python -m build --wheel`