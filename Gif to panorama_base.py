import os
import json
from PIL import Image, ImageSequence
import shutil
import uuid

container_sizes = {
    "inventory1": (176, 166),
    "chest1": (176, 166),
    "doublechest1": (176, 222),
    "barrel1": (176, 166),
    "shulkerbox1": (176, 166),
    "enderchest": (176, 166),
    "hopper1": (176, 133),
    "redstone1": (176, 166),
    "furnace1": (176, 166),
    "brewingstand1": (176, 166),
    "smithingtable1": (176, 166),
    "cartographytable1": (176, 220),
    "loom1": (146, 166),
    "grindstone1": (176, 166),
    "stonecutter1": (176, 166),
    "anvil1": (176, 166),
    "beacon1": (176, 166),
    "enchantmenttable1": (176, 166),
    "horseinventory1": (176, 166),
    "recipebook1": (146, 166),
    "panorama1": (600, 365)
}

def generate_flipbook(gif_path, output_path, container_name):
    container_name = container_name.lower()
    if container_name not in container_sizes:
        print(f"Container name '{container_name}' not found.")
        return

    frame_width, frame_height = container_sizes[container_name]
    gif = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]
    sprite_sheet_height = frame_height * len(frames)
    sprite_sheet = Image.new("RGBA", (frame_width, sprite_sheet_height))

    for index, frame in enumerate(frames):
        resized_frame = frame.resize((frame_width, frame_height))
        sprite_sheet.paste(resized_frame, (0, index * frame_height))

    sprite_sheet_name = os.path.splitext(os.path.basename(gif_path))[0]
    textures_ui_path = os.path.join(output_path, "pack", "textures", "ui")
    os.makedirs(textures_ui_path, exist_ok=True)
    sprite_sheet_path = os.path.join(textures_ui_path, f"{sprite_sheet_name}.png")
    sprite_sheet.save(sprite_sheet_path)

    frames_data = {
        "frames": [
            {
                "filename": f"{sprite_sheet_name} {index}.png",
                "frame": {"x": 0, "y": index * frame_height, "w": frame_width, "h": frame_height},
                "rotated": False,
                "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": frame_width, "h": frame_height},
                "sourceSize": {"w": frame_width, "h": frame_height},
                "duration": 100
            } for index in range(len(frames))
        ],
        "meta": {
            "image": "",
            "format": "RGBA8888",
            "size": {"w": frame_width, "h": sprite_sheet_height},
            "scale": "1",
            "frameTags": [],
            "layers": [{"name": "Background", "opacity": 255, "blendMode": "normal"}]
        }
    }

    frames_file_path = os.path.join(textures_ui_path, f"{sprite_sheet_name}.json")
    with open(frames_file_path, 'w') as frames_file:
        json.dump(frames_data, frames_file, indent=4)

    print(f"Sprite sheet saved to {sprite_sheet_path}")
    print(f"Frames file saved to {frames_file_path}")

    ui_path = os.path.join(output_path, "pack", "ui")
    os.makedirs(ui_path, exist_ok=True)
    ui_file_path = os.path.join(ui_path, f"{sprite_sheet_name}.json")
    uv_size = [710, 365] if container_name == "panorama1" else [frame_width, frame_height]
    ui_data = {
        "namespace": sprite_sheet_name,
        "image_element": {
            "type": "image",
            "texture": f"textures/ui/{sprite_sheet_name}",
            "uv_size": uv_size,
            "uv": f"@{sprite_sheet_name}.image_uv_animation",
            "clip_pixelperfect": "true"
        },
        "image_uv_animation": {
            "anim_type": "aseprite_flip_book",
            "initial_uv": [0, 0]
        }
    }
    with open(ui_file_path, 'w') as ui_file:
        json.dump(ui_data, ui_file, indent=4)

    print(f"UI file saved to {ui_file_path}")

    update_ui_defs(ui_file_path, output_path)

def update_ui_defs(new_ui_file_path, output_path):
    ui_defs_path = os.path.join(output_path, "pack", "ui", "_ui_defs.json")
    if os.path.exists(ui_defs_path):
        with open(ui_defs_path, 'r') as ui_defs_file:
            ui_defs_data = json.load(ui_defs_file)
    else:
        ui_defs_data = {"ui_defs": []}

    relative_ui_file_path = os.path.relpath(new_ui_file_path, os.path.join(output_path, "pack")).replace("\\", "/")
    if relative_ui_file_path not in ui_defs_data["ui_defs"]:
        ui_defs_data["ui_defs"].append(relative_ui_file_path)

    # Add ui/enderchest2.json to ui_defs
    enderchest2_path = "ui/enderchest2.json"
    if enderchest2_path not in ui_defs_data["ui_defs"]:
        ui_defs_data["ui_defs"].append(enderchest2_path)

    with open(ui_defs_path, 'w') as ui_defs_file:
        json.dump(ui_defs_data, ui_defs_file, indent=4)

    print(f"Updated _ui_defs.json with {relative_ui_file_path} and {enderchest2_path}")

def process_gifs_in_folder(folder_path):
    gif_files = [file_name for file_name in os.listdir(folder_path) if file_name.endswith(".gif")]
    for file_name in gif_files:
        container_name = os.path.splitext(file_name)[0].replace('_', '').lower()
        gif_path = os.path.join(folder_path, file_name)
        print(f"Processing GIF: {file_name}")
        generate_flipbook(gif_path, folder_path, container_name)

def copy_json_files(guis_folder, ui_folder):
    if not os.path.exists(guis_folder):
        print(f"Source folder '{guis_folder}' does not exist.")
        return

    os.makedirs(ui_folder, exist_ok=True)
    for file_name in os.listdir(guis_folder):
        if file_name.endswith(".json"):
            src_file_path = os.path.join(guis_folder, file_name)
            dest_file_path = os.path.join(ui_folder, file_name)
            shutil.copy(src_file_path, dest_file_path)
            print(f"Copied {file_name} to {dest_file_path}")

def create_manifest(output_path):
    manifest_data = {
        "format_version": 2,
        "header": {
            "description": "Generated with ashura_tepes anim ui maker",
            "name": "§r§4§l do not distribute without permission!",
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0],
            "min_engine_version": [1, 16, 0]
        },
        "modules": [
            {
                "description": "Generated with ashura_tepes anim ui maker",
                "type": "resources",
                "uuid": str(uuid.uuid4()),
                "version": [1, 0, 0]
            }
        ]
    }
    manifest_path = os.path.join(output_path, "pack", "manifest.json")
    with open(manifest_path, 'w') as manifest_file:
        json.dump(manifest_data, manifest_file, indent=4)
    print(f"Manifest file saved to {manifest_path}")

# Example usage
folder_path = os.path.dirname(os.path.abspath(__file__))
guis_folder = os.path.join(folder_path, "guis")
ui_folder = os.path.join(folder_path, "pack", "ui")
process_gifs_in_folder(folder_path)
copy_json_files(guis_folder, ui_folder)
create_manifest(folder_path)
