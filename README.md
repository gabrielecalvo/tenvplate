# T\<env\>plate

A way to generate `.env` files from a template file using remote sources.

Currently supports the following remote sources:

- azure keyvault secrets
- kubernetes secrets
- kubernetes configmaps

## Usage

1. Install the package, currently only via github `pipx install git+https://github.com/gabrielecalvo/tenvplate.git`

2. Create a .env.template with the following format:

```env
# comment, will be ignored
FIXED=will-be-left-untouched
ENV_VAR_FROM_K8S_SECRET={{kubernetes/<name-space-name>/secrets/<secret-name>/<secret-field>}}
ENV_VAR_FROM_K8S_CONFIGMAP={{kubernetes/<name-space-name>/configmaps/<configmap-name>/<configmap-field>}}
ENV_VAR_FROM_AZURE_KEYVAULT={{azure-keyvault/<keyvault-name>/secrets/<secret-name>}}
```

3. Run the following command to generate a .env file: `python -m tenvplate`
