"""
Generates the missing method for all Enum classes in the specified directory.
"""

import re

patch = """

    @classmethod
    def _missing_(cls, value):
        # Called when `value` doesn't match any member
        return cls.{enum_name}

"""


def apply_patch_to_enum_classes():
    from pathlib import Path
    from os import listdir
    from os.path import isfile, join

    dir_path = (
        Path(__file__).parent
        / "src"
        / "pieces"
        / "_vendor"
        / "pieces_os_client"
        / "models"
    )

    files = [
        f
        for f in listdir(dir_path)
        if isfile(join(dir_path, f)) and f.endswith("_enum.py")
    ]
    for file in files:
        with open(dir_path / file, "a") as f:
            if file == "os_applet_enum.py":
                enum_name = "UNKNOWN_APPLET_MODULE"
            else:
                enum_name = "UNKNOWN"
            f.write(patch.format(enum_name=enum_name))
    for file in files:
        with open(dir_path / file, "r") as f:
            ## Regex to extract the class name
            regex = r"class (\w+)\(str, Enum\):"
            class_name = re.search(regex, f.read())
        test(
            class_name.group(1),
            enum_file="pieces._vendor.pieces_os_client.models." + file[:-3],
        )


def test(enum_class, enum_file):
    # import the enum class
    import importlib

    mod = importlib.import_module(enum_file)
    enum_instance = getattr(mod, enum_class)
    enum_instance("NON_EXISTENT_VALUE")  # Should not error out

    print(f"Enum patch succeeded for {enum_class} in {enum_file}")


if __name__ == "__main__":
    apply_patch_to_enum_classes()
