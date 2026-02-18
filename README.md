[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T21UH4X8)

# Fusion 360 file version as parameter
Fusion 360 add-in to create a number parameter which has the current version of the file. (To use in your model).

Use the code to create a new Add-in. If you enable the plugin, it will create a new parameter in your projects called "version_num" that you can use in your models.

This is good for if you want to add text to your models which reflect the current version of the file.

## Install

- **Fusion UI**
  - Open Fusion.
  - Utilities tab -> Add-Ins -> Scripts and Add-Ins.
  - Add-Ins tab -> "+" (add) -> select the folder containing `AutoVersionParameter.py` and `AutoVersionParameter.manifest`.
  - Select the add-in -> click "Run".
  - (Optional) check "Run on Startup".

## Usage

- When you open/activate a design, the add-in ensures there is a user parameter named `version_num`.
- When you save, `version_num` is updated just before the save completes so it reflects the version number the file will have after saving.

## Packaging (App Store)

- Zip the add-in folder containing at least:
  - `AutoVersionParameter.py`
  - `AutoVersionParameter.manifest`
  - `resources/` (icons/screenshots if used)
  - `LICENSE`
  - `CHANGELOG.md`

## Notes

- This add-in is intended for Fusion designs (Design workspace).
