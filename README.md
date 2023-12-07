
Use Recteg-Grill to interactively control your grill through Home Assistant.

# Notice

This integration is  not in any way, shape, or form supported by Recteq.

This project is largely based off the original codebase put together by @pdugas at https://github.com/pdugas/recteq. Please see that repository for setup instructions until I can get a new set compiled.


**This integration will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from blueprint API.
`switch` | Switch something `True` or `False`.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `integration_blueprint`.
1. Download _all_ the files from the `custom_components/integration_blueprint/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Integration blueprint"ttps://github.com/pdugas/recteq

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)


## Next steps
These are some next steps you may want to look into:
- Add tests
- Add brand images (logo/icon) to https://github.com/home-assistant/brands.
- Create the first release.
- Submit the integration to the [HACS](https://hacs.xyz/docs/publish/start).
