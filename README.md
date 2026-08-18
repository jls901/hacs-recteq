
Use Recteq to interactively control your grill through Home Assistant.

# Notice

This integration is not in any way, shape, or form supported by Recteq.

This project is largely based off the original codebase put together by @pdugas at https://github.com/pdugas/recteq. Please see that repository for setup instructions.

**This integration will set up the following platforms.**

Platform | Description
-- | --
`climate` | Control the grill temperature and power state.
`sensor` | Report the target, actual, and probe temperatures.
`switch` | Turn the grill power on and off.

## Installation

### With [HACS](https://hacs.xyz/docs/publish/start)

1. Add this repository to HACS as a custom repository (category: Integration).
2. Install the **Recteq** integration.
3. Restart Home Assistant.

### Manual

1. Using the tool of your choice, open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder), create a new folder called `recteq`.
4. Download _all_ the files from the `custom_components/recteq/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant.
7. In the HA UI, go to "Settings" -> "Devices and Services", click "+" and search for "Recteq".

## Configuration is done in the UI

## Contributions are welcome!

If you want to contribute to this, please read the [Contribution guidelines](CONTRIBUTING.md).
