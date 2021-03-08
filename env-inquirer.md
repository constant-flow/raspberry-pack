# Environment variables inquirer

- When you add a `env-inquirer.yaml` to your pack, you can ask the user for their input
- The questions can be yes/no, lists or free text – basically most of what [PythonInquirer](https://github.com/CITGuru/PyInquirer) supports
- All answered question's answers will be an environment variables on the Raspberry Pi

## Minimal example

```yaml
environmentVars:
  - type: list
    name: NODE_VERSION
    message: Which version of Node shall be installed?
    choices: ["7", "8"]

  - type: input
    name: NICK_NAME
    message: Which nickname should the user get?
    default: jon doe

  - type: checkbox
    name: ORDER_OPTIONS
    choices:
      - name: cheese
      - name: onions
      - name: ham
    qmark: 🍕
    message: Any extras to your pizza?
```

... so in this example:

- **NODE_VERSION**: list to choose from in order to set the `NODE_VERSION` environment variable, which e.g. another script will read to install the selected version
- **NICK_NAME**: free text can be provided by the user to define the environment variable `NICK_NAME`, by default it will have the `default` value
- **ORDER_OPTIONS**: three options the user can pick any number from. The list of selection will be saves comma separated

The output will be saved to the `.env` file in your Raspberry-Pack location and copied over to the Raspberry. There your can either find it under `/boot/raspberry-pack/.env` or you simply access the environment variables that are registered by Raspberry-Pack. All environment variables are registered during installation, after the final reboot of Raspberry-Pack you have to do this manually.

## Syntax

- The list of questions must be [YAML](https://www.w3schools.io/file/yaml-cheatsheet-syntax/)
- The structure is the same as [PythonInquirer](https://github.com/CITGuru/PyInquirer#examples) requires it
- Only question in the `environmentVars` array will be asked
