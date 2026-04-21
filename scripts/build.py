import os
import zipfile
from typing import Any

import tomllib

instance_config = """
[General]
ConfigVersion=1.3
InstanceType=OneSix
iconKey=icon
name={name}
""".strip()

mmc_pack = """
{
    "components": [
        {
            "important": true,
            "uid": "net.minecraft",
            "version": "{versions_minecraft}"
        },
        {
            "uid": "net.neoforged",
            "version": "{versions_neoforge}"
        },
        {
            "cachedName": "unsup",
            "cachedVersion": "{versions_unsup}",
            "uid": "com.unascribed.unsup"
        }
    ],
    "formatVersion": 1
}
""".strip()

unsup_patch = """
{
	"formatVersion": 1,
	"name": "unsup",
	"uid": "com.unascribed.unsup",
	"version": "{versions_unsup}",
	"+agents": [
		{
			"name": "com.unascribed:unsup:{versions_unsup}",
			"url": "https://repo.sleeping.town"
		}
	]
}
""".strip()

unsup_config = """
version=1
source_format=packwiz
source=http://localhost:8080/pack.toml
preset=minecraft

[branding]
modpack_name={name}
""".strip()

build_directory = "build"


def init_template(template: str, constants: dict[str, Any], prefix=None):
    templated = template
    for key, value in constants.items():
        if isinstance(value, list):
            continue

        if prefix:
            key = f"{prefix}_{key}"

        if isinstance(value, dict):
            templated = init_template(templated, value, key)
        else:
            templated = templated.replace("{" + key + "}", value)
    return templated


def main():
    with open(os.path.join("pack", "pack.toml"), "rb") as pack_file:
        packwiz_pack = tomllib.load(pack_file)

    os.makedirs(build_directory, exist_ok=True)

    with zipfile.ZipFile(
        os.path.join(build_directory, f"{packwiz_pack['name']}.zip"),
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as output_pack:
        with output_pack.open("instance.cfg", "w") as instance_config_file:
            instance_config_file.write(
                init_template(instance_config, packwiz_pack).encode()
            )

        with output_pack.open("mmc-pack.json", "w") as mmc_pack_file:
            mmc_pack_file.write(init_template(mmc_pack, packwiz_pack).encode())

        with output_pack.open(
            "patches/com.unascribed.unsup.json", "w"
        ) as unsup_patch_file:
            unsup_patch_file.write(init_template(unsup_patch, packwiz_pack).encode())

        with output_pack.open(".minecraft/unsup.ini", "w") as unsup_config_file:
            unsup_config_file.write(init_template(unsup_config, packwiz_pack).encode())

        # with output_pack.open("icon.png", "w") as pack_icon_file:
        #     with open("icon.png", "rb") as icon_file:
        #         pack_icon_file.write(icon_file.read())


if __name__ == "__main__":
    main()
